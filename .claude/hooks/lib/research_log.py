"""Research-log library — read/write per-session fetch records.

Hooks call into this to record verified/flagged fetches and to look up
prior fetches when validating skill writes (Stage 4 §2-Sources traceability)
or session end (Stop hook §2-Sources sweep).

State location: .tgf/state/research-logs/{session_id}.json

Each log file is structured as:

    {
      "session_id": "...",
      "started_at": "<ISO timestamp>",
      "fetches": [
        {
          "timestamp": "...",
          "url": "...",
          "source_id": "...",
          "tier": <int>,
          "content_hash": "...",
          "checks": { "M3_schema": "pass|fail|skipped", ... },
          "status": "verified|flagged|blocked-pending-review",
          "findings": [...]
        }
      ],
      "citations_used": [
        {
          "source_id": "...",
          "fetch_index": <int>,
          "used_in_file": "skills/...",
          "rule_or_ap": "..."
        }
      ]
    }

Per docs/RESEARCH-SECURITY.md §5.2 and impl plan §4.4 / §6.9.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from . import common


LOGS_DIR = "research-logs"


def _log_path(session_id: str) -> Path:
    safe = "".join(c for c in session_id if c.isalnum() or c in "-_") or "unknown"
    return common.state_path(LOGS_DIR, f"{safe}.json")


def load(session_id: str) -> dict[str, Any]:
    """Load (or initialize) the research log for a session."""
    path = _log_path(session_id)
    log = common.load_json(path, default=None)
    if log is None:
        log = {
            "session_id": session_id,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "fetches": [],
            "citations_used": [],
        }
    return log


def save(log: dict[str, Any]) -> None:
    """Persist the research log."""
    common.save_json(_log_path(log["session_id"]), log)


def append_fetch(session_id: str, fetch_record: dict[str, Any]) -> int:
    """Append a fetch record to the session log. Returns the fetch index."""
    log = load(session_id)
    log["fetches"].append(fetch_record)
    save(log)
    return len(log["fetches"]) - 1


def record_citation_use(
    session_id: str,
    source_id: str,
    used_in_file: str,
    rule_or_ap: str | None = None,
) -> None:
    """Record that a verified source was cited in a skill file."""
    log = load(session_id)
    fetch_index = None
    for i, fetch in enumerate(log["fetches"]):
        if fetch.get("source_id") == source_id and fetch.get("status") == "verified":
            fetch_index = i
            break
    log["citations_used"].append({
        "source_id": source_id,
        "fetch_index": fetch_index,
        "used_in_file": used_in_file,
        "rule_or_ap": rule_or_ap,
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    save(log)


def get_fetch_by_source(session_id: str, source_id: str) -> dict[str, Any] | None:
    """Return the most recent fetch record for source_id, or None."""
    log = load(session_id)
    matches = [f for f in log["fetches"] if f.get("source_id") == source_id]
    return matches[-1] if matches else None


def is_verified(session_id: str, source_id: str) -> bool:
    """True iff there is at least one fetch for source_id with status='verified'."""
    log = load(session_id)
    return any(
        f.get("source_id") == source_id and f.get("status") == "verified"
        for f in log["fetches"]
    )


def list_session_fetches(session_id: str) -> list[dict[str, Any]]:
    """Return all fetch records for the session (empty list if none)."""
    log = load(session_id)
    return list(log["fetches"])


def status_of(session_id: str, source_id: str) -> str | None:
    """Return the most recent status ('verified'/'flagged'/'blocked-pending-review')
    for source_id in this session, or None if not present."""
    fetch = get_fetch_by_source(session_id, source_id)
    return fetch.get("status") if fetch else None


def all_verified_source_ids() -> set[str]:
    """Union of source_ids with status='verified' across ALL session research logs.

    Provenance persists across sessions: a source verified under hooks in any
    session is pinned, and that pin backs a citation without a fresh fetch. This
    is the cross-session standard the git pre-commit check already uses; the
    in-session hooks call it via is_backed() so all three enforcement points
    agree on what "backed" means.
    """
    verified: set[str] = set()
    logs_dir = common.state_path(LOGS_DIR)
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


def is_backed(
    session_id: str,
    source_id: str,
    verified_union: set[str] | None = None,
) -> bool:
    """True if a cited source may be written/committed without a fresh fetch.

    Provenance-at-authoring model (see docs/citation-provenance-hook-fix-plan.md):
    a source verified in ANY session is backed — the pin persists, so editing a
    skill that already cites it does not re-demand a fetch.

    Safety override: a NEGATIVE finding for source_id in THIS session
    ('flagged' or 'blocked-pending-review' from a re-fetch) overrides the
    historical verification. So a deliberate staleness-audit re-fetch that
    surfaces tampering still blocks the citation — the fresh signal wins over
    the old pin.

    Pass verified_union (from all_verified_source_ids()) to avoid rescanning all
    logs per source when checking several citations.
    """
    current = status_of(session_id, source_id)
    if current in ("flagged", "blocked-pending-review"):
        return False
    if current == "verified":
        return True
    if verified_union is None:
        verified_union = all_verified_source_ids()
    return source_id in verified_union


def _cli() -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="research_log")
    parser.add_argument("--session-id", required=True)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    p_status = sub.add_parser("status")
    p_status.add_argument("--source-id", required=True)
    p_verified = sub.add_parser("is-verified")
    p_verified.add_argument("--source-id", required=True)
    args = parser.parse_args()

    if args.cmd == "show":
        log = load(args.session_id)
        import json
        print(json.dumps(log, indent=2))
        return 0
    if args.cmd == "status":
        result = status_of(args.session_id, args.source_id)
        print(result or "none")
        return 0
    if args.cmd == "is-verified":
        verified = is_verified(args.session_id, args.source_id)
        print("yes" if verified else "no")
        return 0 if verified else 1
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
