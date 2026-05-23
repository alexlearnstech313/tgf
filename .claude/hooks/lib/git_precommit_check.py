"""Git pre-commit defense-in-depth check.

Replays the Stop hook's logic at git layer: staged-file scan for
control-locking changes requiring M8 approval + citation verification
across the union of all session research logs.

Output: writes findings to stderr; exit 0 = OK, exit 1 = block commit.

Invoked by .claude/git-hooks/pre-commit-research-security.sh which itself
is installed into git via `git config core.hooksPath .claude/git-hooks` or
a manual symlink (see hook script header for installation).

Per docs/RESEARCH-SECURITY.md §7.6 and impl plan §5.4 (Stop hook
defense-in-depth replay).
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import citation_parser, common


CONTROL_LOCKING_RE = re.compile(r"^skills/security-[^/]+/(rules|anti-patterns|SKILL)\.md$")
SKILL_MD_RE = re.compile(r"^skills/[^/]+/[^/]*\.md$")


def _staged_files(project_dir: Path) -> list[str]:
    """Files staged for commit (added, copied, modified). Returns repo-relative paths."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=project_dir, capture_output=True, text=True, check=False, timeout=15,
        )
        return [line.strip() for line in out.stdout.splitlines() if line.strip()]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _staged_content(project_dir: Path, rel_path: str) -> str:
    """Return the staged blob content for rel_path (the to-be-committed version)."""
    try:
        out = subprocess.run(
            ["git", "show", f":{rel_path}"],
            cwd=project_dir, capture_output=True, text=True, check=False, timeout=15,
        )
        return out.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _load_m8_approvals() -> list[dict[str, Any]]:
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


def _all_verified_source_ids() -> set[str]:
    """Union of source_ids with status='verified' across ALL session research logs.

    Pre-commit is not bound to a session — any prior session's verified fetch
    suffices for citation traceability at commit time. Stop hook (in-session)
    is the stricter enforcement.
    """
    verified: set[str] = set()
    logs_dir = common.state_path("research-logs")
    if not logs_dir.is_dir():
        return verified
    for path in logs_dir.glob("*.json"):
        log = common.load_json(path, default=None)
        if not isinstance(log, dict):
            continue
        for fetch in log.get("fetches", []) or []:
            if fetch.get("status") == "verified" and fetch.get("source_id"):
                verified.add(fetch["source_id"])
    return verified


def main() -> int:
    project = common.project_dir()
    staged = _staged_files(project)
    if not staged:
        return 0

    approvals = _load_m8_approvals()
    verified_globally = _all_verified_source_ids()

    missing_m8: list[str] = []
    bad_citations: list[tuple[str, list[str]]] = []

    for rel_path in staged:
        if CONTROL_LOCKING_RE.match(rel_path):
            if not any(_approval_covers(a, rel_path) for a in approvals):
                missing_m8.append(rel_path)

        if SKILL_MD_RE.match(rel_path):
            content = _staged_content(project, rel_path)
            if not content:
                continue
            parsed = citation_parser.parse(content)
            unverified_in_file = [
                sid for sid in parsed["canonical_ids"]
                if sid not in verified_globally
            ]
            if unverified_in_file:
                bad_citations.append((rel_path, unverified_in_file))

    if not missing_m8 and not bad_citations:
        return 0

    print("", file=sys.stderr)
    print("research-security pre-commit BLOCKED this commit", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if missing_m8:
        print("", file=sys.stderr)
        print("Control-locking files staged WITHOUT M8 approval:", file=sys.stderr)
        for rel in missing_m8:
            print(f"  - {rel}", file=sys.stderr)
        print("  Add an approval at .tgf/state/m8-approvals/<timestamp>-<change-id>.json", file=sys.stderr)
        print("  (Format per docs/RESEARCH-SECURITY.md §5.5 / impl plan §4.5)", file=sys.stderr)

    if bad_citations:
        print("", file=sys.stderr)
        print("Staged skill files cite sources with no verified research-log entry:", file=sys.stderr)
        for rel, missing_ids in bad_citations:
            print(f"  {rel}", file=sys.stderr)
            for sid in missing_ids:
                print(f"    - {sid}", file=sys.stderr)
        print("", file=sys.stderr)
        print("  Re-fetch the missing sources under hooks (PostToolUse-WebFetch will write", file=sys.stderr)
        print("  a 'verified' research-log entry), OR remove the citations from the file.", file=sys.stderr)

    print("", file=sys.stderr)
    print("To bypass for emergency commits (audit-logged):", file=sys.stderr)
    print("  set TGF_PRECOMMIT_BYPASS=<rationale> in env (do not use lightly).", file=sys.stderr)
    print("", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
