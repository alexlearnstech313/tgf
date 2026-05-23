"""M4 — Prompt-injection pattern detection.

Scans fetched content for known injection signatures: instruction-override
phrases, role-confusion tokens, system-prompt markers, base64-shaped strings
outside code blocks, and zero-width / bidi-override characters (overlaps
with M14 for defense in depth).

CLI:
    python3 -m lib.m4_pattern_detect --content <file>
    cat content | python3 -m lib.m4_pattern_detect

Output JSON: {status, findings: [{pattern, location, severity, snippet}]}.

Per docs/RESEARCH-SECURITY.md §4.2 M4 and impl plan §6.2.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


# Phrase-based injection patterns (case-insensitive, word-boundary aware).
# Each entry: (regex, severity, description).
PHRASE_PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\bignore\s+(?:the\s+)?(?:prior|previous|all|above)\b", re.IGNORECASE),
     "high", "instruction override: 'ignore prior/previous/all/above' phrase"),
    (re.compile(r"\bdisregard\s+(?:the\s+)?(?:prior|previous|all|above)\b", re.IGNORECASE),
     "high", "instruction override: 'disregard prior/previous/all/above' phrase"),
    (re.compile(r"\byou\s+are\s+now\b", re.IGNORECASE),
     "medium", "role override: 'you are now' phrase"),
    (re.compile(r"\byou\s+must\s+now\b", re.IGNORECASE),
     "medium", "role override: 'you must now' phrase"),
    (re.compile(r"\bact\s+as\s+(?:a\s+|an\s+)?(?:different|new|the\s+following)", re.IGNORECASE),
     "medium", "role override: 'act as different/new/...' phrase"),
    (re.compile(r"\bpretend\s+(?:to\s+be|you\s+are)\b", re.IGNORECASE),
     "medium", "role override: 'pretend to be / pretend you are' phrase"),
    (re.compile(r"\bnew\s+instructions?\s*:", re.IGNORECASE),
     "high", "instruction override: 'new instructions:' marker"),
    (re.compile(r"^\s*system\s*:", re.IGNORECASE | re.MULTILINE),
     "high", "role-confusion token: 'System:' line start"),
    (re.compile(r"^\s*assistant\s*:", re.IGNORECASE | re.MULTILINE),
     "high", "role-confusion token: 'Assistant:' line start"),
    (re.compile(r"<\|im_start\|>"),
     "high", "ChatML role token: <|im_start|>"),
    (re.compile(r"<\|im_end\|>"),
     "high", "ChatML role token: <|im_end|>"),
    (re.compile(r"</?(?:system|assistant|user)\b[^>]*>", re.IGNORECASE),
     "medium", "role-tag injection: <system>/<assistant>/<user> tag"),
    (re.compile(r"\bsudo\s+mode\b", re.IGNORECASE),
     "high", "privilege override: 'sudo mode' phrase"),
    (re.compile(r"\bdeveloper\s+mode\b", re.IGNORECASE),
     "medium", "mode-switch: 'developer mode' phrase"),
    (re.compile(r"\bjailbreak\b", re.IGNORECASE),
     "medium", "explicit jailbreak reference"),
    (re.compile(r"###\s*end\s+of\s+(?:document|context|input)", re.IGNORECASE),
     "medium", "context-termination marker"),
]

# Long base64-shaped strings outside code blocks (heuristic; high false-positive,
# so reported at low severity unless very long).
BASE64_RE = re.compile(r"[A-Za-z0-9+/]{80,}={0,2}")

# Invisible characters (overlaps with M14)
INVISIBLE_RE = re.compile(r"[​-‍⁠﻿‪-‮⁦-⁩]")

# Code-block detection (very rough)
CODE_FENCE_RE = re.compile(r"```[\s\S]*?```")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def _redact_codeblocks(text: str) -> str:
    """Replace code-fenced and inline-code regions with whitespace placeholders.

    Preserves character offsets so other findings stay aligned.
    """
    def repl(m: re.Match[str]) -> str:
        return " " * (m.end() - m.start())
    cleaned = CODE_FENCE_RE.sub(repl, text)
    cleaned = INLINE_CODE_RE.sub(repl, cleaned)
    return cleaned


def _snippet(text: str, start: int, end: int, ctx: int = 30) -> str:
    a = max(0, start - ctx)
    b = min(len(text), end + ctx)
    s = text[a:b].replace("\n", "\\n")
    return s


def check(content: str) -> dict[str, Any]:
    """Run M4 pattern detection. Returns findings list and overall status."""
    findings: list[dict[str, Any]] = []

    redacted = _redact_codeblocks(content)

    for regex, severity, description in PHRASE_PATTERNS:
        for match in regex.finditer(redacted):
            findings.append({
                "pattern": description,
                "severity": severity,
                "offset": match.start(),
                "match": match.group(0)[:80],
                "snippet": _snippet(content, match.start(), match.end()),
            })

    for match in INVISIBLE_RE.finditer(content):
        findings.append({
            "pattern": "invisible / bidi-override character (overlaps M14)",
            "severity": "medium",
            "offset": match.start(),
            "match": f"U+{ord(match.group(0)):04X}",
            "snippet": _snippet(content, match.start(), match.end()),
        })

    for match in BASE64_RE.finditer(redacted):
        length = match.end() - match.start()
        severity = "low" if length < 200 else "medium"
        findings.append({
            "pattern": f"long base64-shaped string ({length} chars) outside code blocks",
            "severity": severity,
            "offset": match.start(),
            "match": match.group(0)[:40] + "...",
            "snippet": _snippet(content, match.start(), match.start() + 60),
        })

    status = "flagged" if any(f["severity"] in ("high", "medium") for f in findings) else (
        "low_findings" if findings else "pass"
    )

    return {
        "status": status,
        "findings": findings,
        "count": len(findings),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m4_pattern_detect")
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
