"""Stop hook implementation — Stage 5→6 gate.

Refuses to end the response if:
  (a) any cited source in this session's research log lacks 'verified' status, or
  (b) any control-locking change (rules.md / anti-patterns.md under
      skills/security-*/) lacks an M8 approval artifact covering it.

The hook is the final defense before commit. Pre-commit git hook (Step 17)
is the defense-in-depth replay.

Per docs/RESEARCH-SECURITY.md §5.4 / §7.6 and impl plan §5.4.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import common, research_log


CONTROL_LOCKING_FILE_PATTERNS = [
    re.compile(r"^skills/security-[^/]+/(rules|anti-patterns|SKILL)\.md$"),
]


def _is_control_locking(rel_path: str) -> bool:
    return any(pat.match(rel_path) for pat in CONTROL_LOCKING_FILE_PATTERNS)


def _git_changed_files(project_dir: Path) -> list[str]:
    """Return repo-relative paths of changed-vs-HEAD files (committed work since HEAD too).

    Combines `git diff --name-only HEAD` (uncommitted) with
    `git diff --name-only HEAD origin/HEAD` style isn't reliable across repos,
    so we use `git diff --name-only HEAD` only — that captures the current
    working state vs the last commit. Untracked files added with `git add`
    show via `git diff --cached`. Untracked-unstaged files show via
    `ls-files --others --exclude-standard`.
    """
    paths: set[str] = set()
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=project_dir, capture_output=True, text=True, check=False, timeout=10,
        )
        paths.update(line.strip() for line in out.stdout.splitlines() if line.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            cwd=project_dir, capture_output=True, text=True, check=False, timeout=10,
        )
        paths.update(line.strip() for line in out.stdout.splitlines() if line.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    try:
        out = subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard"],
            cwd=project_dir, capture_output=True, text=True, check=False, timeout=10,
        )
        paths.update(line.strip() for line in out.stdout.splitlines() if line.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return sorted(paths)


def _load_m8_approvals() -> list[dict[str, Any]]:
    """Load every approval JSON under .tgf/state/m8-approvals/."""
    approvals_dir = common.state_path("m8-approvals")
    if not approvals_dir.is_dir():
        return []
    approvals: list[dict[str, Any]] = []
    for path in sorted(approvals_dir.glob("*.json")):
        data = common.load_json(path, default=None)
        if isinstance(data, dict):
            data.setdefault("_source_path", str(path))
            approvals.append(data)
    return approvals


def _approval_covers(approval: dict[str, Any], rel_path: str) -> bool:
    covers = approval.get("covers_files") or []
    if rel_path in covers:
        return True
    abs_candidate = str(common.project_dir() / rel_path)
    if abs_candidate in covers:
        return True
    return False


def _missing_m8_approvals(changed_files: list[str], approvals: list[dict[str, Any]]) -> list[str]:
    """Return the control-locking changed paths that have NO approval covering them."""
    missing: list[str] = []
    for rel in changed_files:
        if not _is_control_locking(rel):
            continue
        if not any(_approval_covers(a, rel) for a in approvals):
            missing.append(rel)
    return missing


def _bad_cited_sources(session_id: str) -> list[tuple[str, str]]:
    """Return (source_id, reason) pairs for cited sources that are not backed.

    "Backed" is the cross-session provenance rule (research_log.is_backed):
    verified in any session AND not flagged/blocked by a re-fetch this session.
    A source verified in a prior session is fine — its pin persists; only a
    never-verified source or a fresh-this-session tamper flag blocks session end.
    """
    log = research_log.load(session_id)
    verified_union = research_log.all_verified_source_ids()
    bad: list[tuple[str, str]] = []
    seen: set[str] = set()
    for citation in log.get("citations_used", []):
        source_id = citation.get("source_id")
        if not source_id or source_id in seen:
            continue
        seen.add(source_id)
        if not research_log.is_backed(session_id, source_id, verified_union):
            current = research_log.status_of(session_id, source_id)
            reason = current if current in ("flagged", "blocked-pending-review") else "not verified in any session"
            bad.append((source_id, reason))
    return bad


def main() -> int:
    payload = common.read_input()

    if payload.get("hook_event_name") != "Stop":
        common.passthrough()

    if payload.get("stop_hook_active") is True:
        common.log_debug(
            "stop",
            "reentrancy_passthrough",
            {"session_id": payload.get("session_id")},
        )
        common.passthrough()

    session_id = payload.get("session_id", "unknown")
    project = common.project_dir()

    bad_cited = _bad_cited_sources(session_id)
    changed_files = _git_changed_files(project)
    approvals = _load_m8_approvals()
    missing_m8 = _missing_m8_approvals(changed_files, approvals)

    if not bad_cited and not missing_m8:
        common.log_debug(
            "stop",
            "passed",
            {
                "session_id": session_id,
                "changed_files": len(changed_files),
                "control_locking_files": sum(1 for p in changed_files if _is_control_locking(p)),
                "approvals_on_file": len(approvals),
            },
        )
        common.passthrough()

    reason_lines = [
        "Cannot end response — research-security state is inconsistent.",
        "",
    ]
    if bad_cited:
        reason_lines.append("Cited sources lacking 'verified' research-log status:")
        for sid, status in bad_cited:
            reason_lines.append(f"  - {sid}: {status}")
        reason_lines.append("")
    if missing_m8:
        reason_lines.append(
            "Control-locking changes (rules.md / anti-patterns.md / SKILL.md "
            "under skills/security-*/) lacking M8 approval:"
        )
        for rel in missing_m8:
            reason_lines.append(f"  - {rel}")
        reason_lines.append("")
        reason_lines.extend([
            "To resolve, write an M8 approval at "
            ".tgf/state/m8-approvals/<timestamp>-<change-id>.json with:",
            '  {"approval_id": "...", "approved_at": "...", "approved_by": "...",',
            '   "session_id": "<this-session>", "covers_files": [<paths above>],',
            '   "evidence": {"primary_source": {...}, "corroborating_source": {...},',
            '                "independence_check": "pass", "memory_alignment_note": "...",',
            '                "drift_check": "..."}}',
            "(Format per docs/RESEARCH-SECURITY.md §5.5 and impl plan §4.5.)",
        ])

    common.log_debug(
        "stop",
        "block",
        {
            "session_id": session_id,
            "bad_cited_count": len(bad_cited),
            "missing_m8_count": len(missing_m8),
        },
    )

    common.block_stop("\n".join(reason_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
