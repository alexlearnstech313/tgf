"""PreToolUse hook implementation for Write/Edit/MultiEdit on skills/**.

Blocks any write/edit to a skill file when its post-edit content cites a
source that has not been verified in this session's research log.

This is the framework's Stage 4 §2-Sources traceability enforcement. The
structural complement to the user's manual catch on commit 4/12: external,
mechanical, unbypassable except via documented override.

Per docs/RESEARCH-SECURITY.md §5.1 / §7.4 (THE BLOCKING POINT) and impl plan §5.3.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from . import citation_parser, common, research_log, source_registry


SKILLS_PREFIX = "skills/"


def _is_under_skills(file_path: str) -> bool:
    """True if file_path lives under skills/** in the project tree."""
    if not file_path:
        return False
    try:
        abs_path = Path(file_path).resolve()
    except (ValueError, OSError):
        return False
    try:
        rel = abs_path.relative_to(common.project_dir())
    except ValueError:
        return False
    return str(rel).startswith(SKILLS_PREFIX) or str(rel) == "skills"


def _is_markdown(file_path: str) -> bool:
    return file_path.endswith(".md") or file_path.endswith(".MD")


def _read_existing(file_path: str) -> str:
    p = Path(file_path)
    if not p.is_file():
        return ""
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def _apply_edit(content: str, old: str, new: str, replace_all: bool) -> str | None:
    """Apply a single Edit-style replacement. Returns None if old_string not found."""
    if not old:
        return content
    if replace_all:
        return content.replace(old, new)
    if old not in content:
        return None
    return content.replace(old, new, 1)


def _compute_effective_content(tool_name: str, tool_input: dict[str, Any]) -> str | None:
    """Compute the file content as it would exist after the tool call.

    Returns None if the operation is malformed (e.g., Edit old_string not present).
    Returns the resulting markdown content for citation parsing.
    """
    file_path = tool_input.get("file_path", "")
    if tool_name == "Write":
        return tool_input.get("content", "")
    if tool_name == "Edit":
        existing = _read_existing(file_path)
        old = tool_input.get("old_string", "")
        new = tool_input.get("new_string", "")
        replace_all = bool(tool_input.get("replace_all", False))
        return _apply_edit(existing, old, new, replace_all)
    if tool_name == "MultiEdit":
        content = _read_existing(file_path)
        for edit in tool_input.get("edits", []) or []:
            content = _apply_edit(
                content,
                edit.get("old_string", ""),
                edit.get("new_string", ""),
                bool(edit.get("replace_all", False)),
            )
            if content is None:
                return None
        return content
    return None


def _classify_citations(
    canonical_ids: list[str],
    session_id: str,
) -> tuple[list[str], list[str], dict[str, str]]:
    """Bucket canonical citation IDs by whether their provenance backs a write.

    A citation is *backed* if its source is verified in ANY session's research
    log (provenance persists — the pin from when the skill was built carries
    forward) AND it is not flagged/blocked by a re-fetch THIS session (a fresh
    tamper finding overrides the old pin). See research_log.is_backed().

    Returns (backed_ids, unbacked_ids, statuses) where statuses maps source_id
    to a human-readable reason.
    """
    verified_union = research_log.all_verified_source_ids()
    backed: list[str] = []
    unbacked: list[str] = []
    statuses: dict[str, str] = {}
    for source_id in canonical_ids:
        current = research_log.status_of(session_id, source_id)
        if research_log.is_backed(session_id, source_id, verified_union):
            backed.append(source_id)
            statuses[source_id] = (
                "verified this session"
                if current == "verified"
                else "verified in a prior session (provenance persists)"
            )
        else:
            unbacked.append(source_id)
            if current in ("flagged", "blocked-pending-review"):
                statuses[source_id] = (
                    f"{current} by a re-fetch THIS session — the fresh finding "
                    "overrides any prior verification"
                )
            else:
                statuses[source_id] = "not verified in any session"
    return backed, unbacked, statuses


def _check_override(session_id: str, file_path: str) -> bool:
    """Check for an active hook-override that suspends this check.

    Override file format: .tgf/state/hook-overrides/{session_id}-pretool-write.json
    Existence + active=true grants a pass. Per impl plan §10.1 — override is
    logged for audit; this hook merely reads the override decision.
    """
    override_path = common.state_path("hook-overrides", f"{session_id}-pretool-write.json")
    data = common.load_json(override_path, default=None)
    if not data:
        return False
    if not data.get("active"):
        return False
    covered = data.get("covers_files") or []
    if covered and file_path not in covered:
        return False
    return True


def main() -> int:
    payload = common.read_input()

    if payload.get("hook_event_name") != "PreToolUse":
        common.passthrough()

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "MultiEdit"):
        common.passthrough()

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "")
    if not _is_under_skills(file_path) or not _is_markdown(file_path):
        common.passthrough()

    session_id = payload.get("session_id", "unknown")

    if _check_override(session_id, file_path):
        common.log_debug(
            "pretool_write",
            "override_active",
            {"session_id": session_id, "file_path": file_path},
        )
        common.passthrough()

    effective = _compute_effective_content(tool_name, tool_input)
    if effective is None:
        common.log_debug(
            "pretool_write",
            "malformed_edit",
            {"session_id": session_id, "tool_name": tool_name, "file_path": file_path},
        )
        common.passthrough()

    parsed = citation_parser.parse(effective)
    canonical_ids = parsed["canonical_ids"]

    if not canonical_ids:
        common.log_debug(
            "pretool_write",
            "no_citations",
            {"session_id": session_id, "file_path": file_path},
        )
        common.passthrough()

    backed, unbacked, statuses = _classify_citations(canonical_ids, session_id)

    if unbacked:
        common.log_debug(
            "pretool_write",
            "deny",
            {
                "session_id": session_id,
                "file_path": file_path,
                "tool_name": tool_name,
                "unbacked": unbacked,
                "backed": backed,
            },
        )
        status_lines = [f"  - {sid}: {statuses[sid]}" for sid in unbacked]
        common.deny_pretool(
            "Write blocked by research-security §2-Sources traceability check (Stage 4).\n"
            f"File: {file_path}\n"
            f"Tool: {tool_name}\n"
            "Citations not backed by verified provenance:\n"
            + "\n".join(status_lines)
            + "\n\nProvenance persists across sessions — a source verified under hooks in "
              "ANY prior session backs the citation without a re-fetch. A block here means "
              "the source was either never verified anywhere, or a re-fetch THIS session "
              "flagged it.\n\nOptions:\n"
              "  (1) If never verified: fetch the source once under hooks (PostToolUse-WebFetch "
              "records a 'verified' entry) — this is authoring-time provenance.\n"
              "  (2) If flagged this session: investigate the tamper finding before citing; do "
              "not blindly re-baseline a genuine flag.\n"
              "  (3) Remove the citation from the file.\n"
              "  (4) Write a human override at "
              f".tgf/state/hook-overrides/{session_id}-pretool-write.json "
              "with {\"active\": true, \"rationale\": \"...\", "
              "\"covers_files\": [\"<this path>\"], \"reviewer\": \"...\"} "
              "(audit-logged per impl plan §10.1)"
        )

    for source_id in backed:
        try:
            research_log.record_citation_use(session_id, source_id, file_path, None)
        except Exception:
            pass

    common.log_debug(
        "pretool_write",
        "approved",
        {
            "session_id": session_id,
            "file_path": file_path,
            "tool_name": tool_name,
            "backed": backed,
        },
    )
    common.passthrough()
    return 0


if __name__ == "__main__":
    sys.exit(main())
