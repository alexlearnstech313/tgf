"""SessionStart hook implementation.

Verifies that .tgf/state/ infrastructure is present and injects research-security
context into the AI session. Cannot block (SessionStart never blocks); always
exits 0. If state is missing, warns via additionalContext rather than failing
silently.
"""

from __future__ import annotations

import sys

from . import common


def main() -> int:
    payload = common.read_input()
    event = payload.get("hook_event_name", "SessionStart")

    if event not in ("SessionStart", ""):
        common.passthrough()

    state_dir = common.state_path()
    issues: list[str] = []
    if not state_dir.is_dir():
        issues.append(f"state directory missing: {state_dir}")
    else:
        for fname in (
            "source-registry.json",
            "source-hashes.json",
            "source-org-mapping.json",
            "parameter-history.json",
            "baseline-updates.json",
        ):
            if not (state_dir / fname).is_file():
                issues.append(f"missing: {fname}")

    lines: list[str] = ["Research-security enforcement active (M1-M19; see docs/RESEARCH-SECURITY.md)."]
    if issues:
        lines.append("WARNING: research-security state setup incomplete:")
        lines.extend(f"  - {issue}" for issue in issues)
        lines.append(
            "Hooks will operate in degraded mode until resolved. "
            "Run the research-security implementation plan Step 1 bootstrap if state is missing."
        )

    lines.extend([
        "- M15 URL allow-list: WebFetch URLs are checked against .tgf/state/source-registry.json before fetch",
        "- M3/M4/M11/M13/M14/M18/M19: fetched content is scanned for schema/pattern/drift/hash/unicode/exception/hidden findings (PostToolUse warns + records to research-log)",
        "- §2-Sources traceability: Write/Edit to skills/** blocked if citations lack verified research-log entries (Stage 4 enforcement)",
        "- M9 (memory-confirmation gap): AI prior knowledge consistent with a fetched source is ONE source of evidence, NOT two",
        "- M8: control-locking parameter changes require explicit human approval recorded in .tgf/state/m8-approvals/",
    ])

    common.log_debug("session_start", "context_injected", {"issues": issues})

    common.write_response({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n".join(lines),
        }
    })
    return 0


if __name__ == "__main__":
    sys.exit(main())
