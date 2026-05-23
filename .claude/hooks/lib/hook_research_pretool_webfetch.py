"""PreToolUse hook implementation for WebFetch (M15 URL allow-list).

Reads the PreToolUse JSON payload from stdin. If the WebFetch URL matches an
entry in .tgf/state/source-registry.json (via lookup_url), records pretool
context to .tgf/state/pretool-context/{session_id}.json for PostToolUse to
consume and exits 0. If the URL does not match, emits a permissionDecision:
deny response with reason.

This is the first blocking layer in the research-security architecture
(RESEARCH-SECURITY.md §5.1 / impl plan §5.1).
"""

from __future__ import annotations

import sys
import time

from . import common, source_registry


def main() -> int:
    payload = common.read_input()

    if payload.get("hook_event_name") != "PreToolUse":
        common.passthrough()
    if payload.get("tool_name") != "WebFetch":
        common.passthrough()

    tool_input = payload.get("tool_input", {}) or {}
    url = (tool_input.get("url") or "").strip()
    session_id = payload.get("session_id", "unknown")

    if not url:
        common.log_debug(
            "pretool_webfetch",
            "missing_url",
            {"session_id": session_id, "tool_input": tool_input},
        )
        common.passthrough()

    matched_source_id = source_registry.lookup_url(url)

    if matched_source_id is None:
        common.log_debug(
            "pretool_webfetch",
            "deny",
            {"session_id": session_id, "url": url, "reason": "url_not_in_registry"},
        )
        common.deny_pretool(
            f"WebFetch blocked by research-security M15 (URL allow-list).\n"
            f"URL: {url}\n"
            f"This URL does not match any allow_url_patterns in .tgf/state/source-registry.json.\n"
            f"To approve: add an entry under sources.<SOURCE_ID> with tier, type, publisher, "
            f"jurisdiction, primary_url, and allow_url_patterns covering this URL pattern."
        )

    meta = source_registry.get_source(matched_source_id) or {}
    hashes_data = common.load_json(
        common.state_path("source-hashes.json"),
        default={"hashes": {}},
    )
    pinned_hash = (
        hashes_data.get("hashes", {})
        .get(matched_source_id, {})
        .get("sha256")
    )

    pretool_context = {
        "session_id": session_id,
        "source_id": matched_source_id,
        "url": url,
        "tier": meta.get("tier"),
        "type": meta.get("type"),
        "publisher": meta.get("publisher"),
        "jurisdiction": meta.get("jurisdiction"),
        "expected_schema": meta.get("expected_schema"),
        "pinned_hash": pinned_hash,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    common.save_json(
        common.state_path("pretool-context", f"{session_id}.json"),
        pretool_context,
    )
    common.log_debug(
        "pretool_webfetch",
        "approved",
        {"session_id": session_id, "source_id": matched_source_id, "url": url},
    )
    common.passthrough()
    return 0


if __name__ == "__main__":
    sys.exit(main())
