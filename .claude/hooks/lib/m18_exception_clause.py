"""M18 — Exception-clause pattern detection.

Scans for "except when...", "unless...", "in [context], [weaker] is
acceptable" style patterns in security guidance text. Not always malicious —
sometimes legitimate scope notes — but warrants explicit human review at
Stage 3 per RESEARCH-SECURITY.md §4.2 M18.

CLI:
    python3 -m lib.m18_exception_clause --content <file>

Output JSON: {status, findings: [{pattern, location, severity, snippet}]}.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


# Exception-clause patterns. Severity is informational — flag for review,
# not automatic block.
EXCEPTION_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\bexcept\s+(?:when|where|in|if|for|that|as|under|during)\b", re.IGNORECASE),
     "medium", "exception clause: 'except when/where/in/if/for/that/as/under/during'"),
    (re.compile(r"\bunless\b", re.IGNORECASE),
     "low", "conditional exception: 'unless'"),
    (re.compile(r"\bwith\s+the\s+exception\s+of\b", re.IGNORECASE),
     "medium", "explicit exception: 'with the exception of'"),
    (re.compile(r"\bthe\s+following\s+exceptions?\s+apply\b", re.IGNORECASE),
     "high", "exception list marker: 'the following exception(s) apply'"),
    (re.compile(r"\bnot\s+required\s+(?:when|if|for|in|where|under)\b", re.IGNORECASE),
     "high", "requirement waiver: 'not required when/if/for/in/where/under'"),
    (re.compile(r"\bmay\s+be\s+(?:omitted|skipped|relaxed|waived|reduced|disabled)\b", re.IGNORECASE),
     "high", "requirement waiver: 'may be omitted/skipped/relaxed/waived/reduced/disabled'"),
    (re.compile(r"\bis\s+acceptable\s+(?:when|if|for|in|where|under)\b", re.IGNORECASE),
     "high", "weakening: '[weaker option] is acceptable when/if/for/in/where/under'"),
    (re.compile(r"\bis\s+permitted\s+(?:when|if|for|in|where|under)\b", re.IGNORECASE),
     "high", "weakening: '[weaker option] is permitted when/if/for/in/where/under'"),
    (re.compile(r"\bfor\s+(?:legacy|internal|admin|trusted|backward)\s+(?:systems?|use|compatibility|users?|clients?)\b", re.IGNORECASE),
     "medium", "scope carve-out: 'for legacy/internal/admin/trusted/backward [context]'"),
    (re.compile(r"\bin\s+(?:non[- ]?production|development|test|staging)\s+(?:environments?|systems?)\b", re.IGNORECASE),
     "medium", "environment carve-out: 'in non-production/development/test/staging'"),
]


def _snippet(text: str, start: int, end: int, ctx: int = 60) -> str:
    a = max(0, start - ctx)
    b = min(len(text), end + ctx)
    s = text[a:b].replace("\n", " ")
    return s


def check(content: str) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for regex, severity, description in EXCEPTION_PATTERNS:
        for match in regex.finditer(content):
            findings.append({
                "pattern": description,
                "severity": severity,
                "offset": match.start(),
                "match": match.group(0),
                "snippet": _snippet(content, match.start(), match.end()),
            })

    if not findings:
        status = "pass"
    elif any(f["severity"] == "high" for f in findings):
        status = "flagged"
    else:
        status = "low_findings"

    return {
        "status": status,
        "findings": findings,
        "count": len(findings),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m18_exception_clause")
    parser.add_argument("--content", help="Path to content file (default: stdin)")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = check(text)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("pass", "low_findings") else 1


if __name__ == "__main__":
    sys.exit(_cli())
