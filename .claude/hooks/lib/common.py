"""Shared utilities for research-security hook scripts.

Provides hook I/O helpers (read input, emit structured responses), path
resolution, debug logging, and JSON response builders aligned with the Claude
Code hook contract verified 2026-05-22 via claude-code-guide agent.

Importable as `from lib.common import ...` when hook scripts add this
directory to sys.path, and runnable as a CLI smoke test:

    python3 -m lib.common --self-test
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any


HOOK_DEBUG_LOG = "hook-debug.log"
STATE_DIR_NAME = ".tgf/state"
HOOKS_DIR_NAME = ".claude/hooks"


def project_dir() -> Path:
    """Resolve the TGF project root.

    Prefers ``CLAUDE_PROJECT_DIR`` (Claude Code sets this when running hooks).
    Falls back to walking up from this file until a directory containing
    ``.claude/`` or ``.git/`` is found.
    """
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        p = Path(env_dir).resolve()
        if p.is_dir():
            return p

    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / ".claude").is_dir() or (parent / ".git").is_dir():
            return parent
    return Path.cwd().resolve()


def state_path(*parts: str) -> Path:
    """Join the .tgf/state path with optional sub-parts."""
    return project_dir().joinpath(STATE_DIR_NAME, *parts)


def hooks_path(*parts: str) -> Path:
    """Join the .claude/hooks path with optional sub-parts."""
    return project_dir().joinpath(HOOKS_DIR_NAME, *parts)


def read_input() -> dict[str, Any]:
    """Read the hook input JSON from stdin.

    Claude Code provides hook context as a single JSON object on stdin.
    Returns an empty dict on stdin EOF or unparseable input (hook scripts
    should treat that as a no-op pass-through, not a block).
    """
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        log_debug("read_input", "stdin_unparseable", {"raw_len": len(raw)})
        return {}


def write_response(obj: dict[str, Any]) -> None:
    """Write a JSON response to stdout (no trailing newline assumptions)."""
    sys.stdout.write(json.dumps(obj))
    sys.stdout.flush()


def deny_pretool(reason: str, event: str = "PreToolUse") -> None:
    """Emit a PreToolUse permission deny response and exit 0.

    Per Claude Code hook contract, PreToolUse blocks via:
        {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "<reason>"
        }}
    """
    write_response({
        "hookSpecificOutput": {
            "hookEventName": event,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    })
    sys.exit(0)


def add_context(message: str, event: str = "PostToolUse") -> None:
    """Emit a PostToolUse additionalContext response and exit 0.

    PostToolUse cannot block but can inject context that the model receives
    as part of the next turn. Used by the research-posttool-webfetch hook to
    warn about flagged fetches without blocking the model.
    """
    write_response({
        "hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": message,
        }
    })
    sys.exit(0)


def block_stop(reason: str) -> None:
    """Emit a Stop hook block response and exit 0.

    Per Claude Code hook contract, the Stop event blocks via:
        {"decision": "block", "reason": "<reason>"}
    """
    write_response({"decision": "block", "reason": reason})
    sys.exit(0)


def passthrough() -> None:
    """Exit 0 with no output (pass-through, no opinion)."""
    sys.exit(0)


def log_debug(component: str, event: str, payload: dict[str, Any] | None = None) -> None:
    """Append a structured debug entry to .tgf/state/hook-debug.log.

    Best-effort — never raises. Hooks log here for post-hoc diagnosis when
    Claude Code's own hook stderr capture isn't sufficient.
    """
    try:
        log_path = state_path(HOOK_DEBUG_LOG)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "component": component,
            "event": event,
            "payload": payload or {},
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def load_json(path: Path, default: Any = None) -> Any:
    """Load a JSON file with a default fallback if missing or unparseable."""
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, data: Any) -> None:
    """Write JSON to a file, creating parent directories as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _self_test() -> int:
    """Smoke-check that path resolution and logging work end-to-end."""
    pd = project_dir()
    sp = state_path()
    hp = hooks_path()
    assert pd.is_dir(), f"project_dir not a directory: {pd}"
    assert sp.is_dir(), f"state_path not a directory: {sp}"
    assert hp.is_dir(), f"hooks_path not a directory: {hp}"
    log_debug("common", "self_test", {"project_dir": str(pd)})
    print(json.dumps({
        "project_dir": str(pd),
        "state_path": str(sp),
        "hooks_path": str(hp),
    }, indent=2))
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(_self_test())
    print("common.py — library module. Use --self-test to verify.", file=sys.stderr)
    sys.exit(1)
