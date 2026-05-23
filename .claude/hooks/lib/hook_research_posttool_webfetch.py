"""PostToolUse hook implementation for WebFetch.

Consumes the pretool-context handoff written by PreToolUse, extracts fetched
content from tool_response, runs all 7 M-helpers (M3/M4/M11/M13/M14/M18/M19)
serially, composes a research-log entry with overall status, and emits an
additionalContext warning when findings are present.

PostToolUse CANNOT block. The fetch already happened; this hook records the
verdict so PreToolUse-Write (Stage 4) can refuse to cite a flagged source.

Per docs/RESEARCH-SECURITY.md §5.1 / §7.1 (post-fetch flow) and impl plan §5.2.
"""

from __future__ import annotations

import hashlib
import sys
import time
from typing import Any

from . import (
    common,
    m3_schema_validate,
    m4_pattern_detect,
    m11_drift_detect,
    m13_hash_check,
    m14_unicode_normalize,
    m18_exception_clause,
    m19_html_hidden,
    research_log,
)


PRETOOL_CONTEXT_DIR = "pretool-context"
BASELINES_DIR = "source-baselines"


def _extract_content(tool_response: Any) -> str:
    """Best-effort extraction of WebFetch content from tool_response.

    The WebFetch tool's response shape on Claude Code includes a structured
    JSON with content. Handle both string and dict response shapes defensively.
    """
    if tool_response is None:
        return ""
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        for key in ("content", "text", "body", "response"):
            value = tool_response.get(key)
            if isinstance(value, str):
                return value
            if isinstance(value, list):
                parts = [v if isinstance(v, str) else v.get("text", "") for v in value]
                return "\n".join(p for p in parts if p)
        return str(tool_response)
    return str(tool_response)


def _looks_like_html(text: str, source_type: str | None) -> bool:
    if source_type in ("owasp-cheat-sheet", "owasp-top-10", "owasp-llm-top-10", "mitre-cwe"):
        return True
    if source_type in ("nist-sp", "nist-fips"):
        return False
    head = text.lstrip()[:200].lower()
    return "<html" in head or "<!doctype html" in head


def _load_baseline(source_id: str) -> str | None:
    path = common.state_path(BASELINES_DIR, f"{source_id}.md")
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _load_schema(schema_id: str | None) -> dict[str, Any] | None:
    if not schema_id:
        return None
    return common.load_json(
        common.state_path("source-schemas", f"{schema_id}.json"),
        default=None,
    )


def _pin_hash_if_missing(source_id: str, content_hash: str, url: str) -> bool:
    """Write the pinned hash if no hash is pinned yet for this source."""
    hashes_path = common.state_path("source-hashes.json")
    data = common.load_json(hashes_path, default={"version": 1, "hashes": {}})
    if source_id in data.get("hashes", {}):
        return False
    data.setdefault("hashes", {})[source_id] = {
        "sha256": content_hash,
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "url_at_capture": url,
    }
    common.save_json(hashes_path, data)
    return True


def _overall_status(check_results: dict[str, Any]) -> tuple[str, list[str]]:
    """Compute overall verdict from per-check results. Returns (status, findings_summary)."""
    findings: list[str] = []
    severity_bumps = 0
    block_pending = False

    m13 = check_results.get("M13_hash", {})
    if m13.get("status") == "fail":
        block_pending = True
        findings.append(m13.get("finding") or "M13 hash mismatch")

    m14 = check_results.get("M14_unicode", {})
    if m14.get("status") == "flagged":
        severity_bumps += 1
        findings.extend(m14.get("findings", []))

    m4 = check_results.get("M4_patterns", {})
    if m4.get("status") == "flagged":
        for f in m4.get("findings", []):
            sev = f.get("severity", "low")
            label = f.get("pattern", "M4 finding")
            findings.append(f"M4 ({sev}): {label}")
            if sev == "high":
                severity_bumps += 2
            elif sev == "medium":
                severity_bumps += 1
    elif m4.get("status") == "low_findings":
        findings.append(f"M4: {m4.get('count', 0)} low-severity finding(s)")

    m3 = check_results.get("M3_schema", {})
    if m3.get("status") == "fail":
        block_pending = True
        for f in m3.get("findings", []):
            findings.append(f)

    m11 = check_results.get("M11_drift", {})
    if m11.get("status") == "drift_high":
        severity_bumps += 2
        findings.append(m11.get("summary") or "M11 high drift")
    elif m11.get("status") == "drift_low":
        findings.append(m11.get("summary") or "M11 low drift")

    m18 = check_results.get("M18_exception", {})
    if m18.get("status") == "flagged":
        severity_bumps += 1
        for f in m18.get("findings", []):
            findings.append(f"M18 ({f.get('severity', 'med')}): {f.get('pattern', 'exception clause')}")
    elif m18.get("status") == "low_findings":
        findings.append(f"M18: {m18.get('count', 0)} low-severity exception phrase(s)")

    m19 = check_results.get("M19_html_hidden", {})
    if m19.get("status") == "flagged":
        severity_bumps += 1
        for f in m19.get("hidden_content", []):
            findings.append(f"M19: {f.get('element')} — {f.get('reason')}")

    if block_pending:
        return "blocked-pending-review", findings
    if severity_bumps >= 2 or any("M4 (high)" in f for f in findings):
        return "flagged", findings
    if findings:
        return "flagged", findings
    return "verified", findings


def main() -> int:
    payload = common.read_input()

    if payload.get("hook_event_name") != "PostToolUse":
        common.passthrough()
    if payload.get("tool_name") != "WebFetch":
        common.passthrough()

    session_id = payload.get("session_id", "unknown")
    tool_input = payload.get("tool_input", {}) or {}
    tool_response = payload.get("tool_response")

    url = (tool_input.get("url") or "").strip()

    pretool_path = common.state_path(PRETOOL_CONTEXT_DIR, f"{session_id}.json")
    pretool = common.load_json(pretool_path, default=None) or {}

    source_id = pretool.get("source_id")
    source_type = pretool.get("type")
    schema_id = pretool.get("expected_schema")
    pinned_hash = pretool.get("pinned_hash")
    tier = pretool.get("tier")

    if not source_id:
        common.log_debug(
            "posttool_webfetch",
            "no_pretool_context",
            {"session_id": session_id, "url": url},
        )
        common.passthrough()

    raw_content = _extract_content(tool_response)
    if not raw_content:
        common.log_debug(
            "posttool_webfetch",
            "empty_content",
            {"session_id": session_id, "url": url, "source_id": source_id},
        )
        common.add_context(
            f"WebFetch returned empty/unreadable content for {source_id} ({url}). "
            f"Research-security checks could not run. Re-fetch or treat as unverified.",
            event="PostToolUse",
        )

    m14_result = m14_unicode_normalize.check(raw_content)
    normalized = m14_result["normalized_content"]
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    m13_result = m13_hash_check.check(normalized, pinned_hash)
    m4_result = m4_pattern_detect.check(normalized)
    m18_result = m18_exception_clause.check(normalized)

    schema = _load_schema(schema_id)
    m3_result = m3_schema_validate.check(normalized, schema)

    if _looks_like_html(raw_content, source_type):
        m19_result = m19_html_hidden.check(raw_content)
    else:
        m19_result = {"status": "skipped", "reason": "non-HTML source", "hidden_content": []}

    baseline = _load_baseline(source_id)
    m11_result = m11_drift_detect.check(normalized, baseline)

    check_summary = {
        "M3_schema": {"status": m3_result["status"], "findings": m3_result.get("findings", [])},
        "M4_patterns": {"status": m4_result["status"], "count": m4_result.get("count", 0),
                        "findings": m4_result.get("findings", [])},
        "M11_drift": {"status": m11_result["status"], "summary": m11_result.get("summary"),
                      "lines_changed": m11_result.get("lines_changed", 0),
                      "structural_changes": m11_result.get("structural_changes", 0)},
        "M13_hash": {"status": m13_result["status"], "finding": m13_result.get("finding")},
        "M14_unicode": {"status": m14_result["status"], "stripped": m14_result.get("stripped_count", 0),
                        "findings": m14_result.get("findings", [])},
        "M18_exception": {"status": m18_result["status"], "count": m18_result.get("count", 0),
                          "findings": m18_result.get("findings", [])},
        "M19_html_hidden": {"status": m19_result["status"],
                            "hidden_content": m19_result.get("hidden_content", [])},
    }

    status, findings_summary = _overall_status(check_summary)

    pinned_now = False
    baseline_now = False
    if status == "verified":
        if not pinned_hash:
            pinned_now = _pin_hash_if_missing(source_id, content_hash, url)
        if baseline is None:
            baseline_now = True
            path = common.state_path(BASELINES_DIR, f"{source_id}.md")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(normalized, encoding="utf-8")

    fetch_record = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "url": url,
        "source_id": source_id,
        "tier": tier,
        "content_hash": content_hash,
        "checks": check_summary,
        "status": status,
        "findings": findings_summary,
        "first_pinning": pinned_now,
        "first_baseline": baseline_now,
    }
    fetch_index = research_log.append_fetch(session_id, fetch_record)

    try:
        pretool_path.unlink(missing_ok=True)
    except Exception:
        pass

    common.log_debug(
        "posttool_webfetch",
        status,
        {
            "session_id": session_id,
            "source_id": source_id,
            "url": url,
            "fetch_index": fetch_index,
            "finding_count": len(findings_summary),
        },
    )

    if status == "verified":
        msg_lines = [
            f"WebFetch VERIFIED — {source_id} ({url})",
            f"All research-security checks passed. Fetch index {fetch_index} in session research log.",
        ]
        if pinned_now:
            msg_lines.append(f"First pinning of {source_id}: SHA-256 recorded.")
        if baseline_now:
            msg_lines.append(f"First baseline of {source_id}: stored for future M11 drift checks.")
        common.add_context("\n".join(msg_lines), event="PostToolUse")

    head = "FLAGGED" if status == "flagged" else "BLOCKED-PENDING-REVIEW"
    msg_lines = [
        f"WebFetch {head} — {source_id} ({url})",
        "Research-security checks produced findings:",
    ]
    msg_lines.extend(f"  - {f}" for f in findings_summary[:20])
    if len(findings_summary) > 20:
        msg_lines.append(f"  ... and {len(findings_summary) - 20} more")
    msg_lines.extend([
        "",
        f"This fetch is recorded in .tgf/state/research-logs/{session_id}.json (fetch index {fetch_index}) with status: {status}.",
        "Do NOT cite this source in skill files until findings are resolved. Re-fetch from a verified URL, "
        "remove the citation, or request human override via /tgf:override-citation (logged to .tgf/state/hook-overrides/).",
    ])
    common.add_context("\n".join(msg_lines), event="PostToolUse")
    return 0


if __name__ == "__main__":
    sys.exit(main())
