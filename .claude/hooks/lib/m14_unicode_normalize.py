"""M14 — Unicode normalization with homoglyph and bidi-override detection.

NFC-normalizes content, strips invisible characters (zero-width, bidi
override), and flags mixed-script "words" that may be homoglyph attacks
(e.g., Cyrillic 'А' substituted for Latin 'A' in an identifier).

CLI:
    python3 -m lib.m14_unicode_normalize --content <file>
    cat content | python3 -m lib.m14_unicode_normalize

Output JSON: {status, original_length, normalized_length, stripped_count,
flagged_tokens, normalized_content}.

Per docs/RESEARCH-SECURITY.md §4.2 M14 and impl plan §6.5.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from typing import Any


# Zero-width and BOM characters (M14 §4.2)
ZERO_WIDTH = {
    "​",  # ZERO WIDTH SPACE
    "‌",  # ZERO WIDTH NON-JOINER
    "‍",  # ZERO WIDTH JOINER
    "⁠",  # WORD JOINER
    "﻿",  # ZERO WIDTH NO-BREAK SPACE / BOM
}

# Bidi-override and isolate characters (M14 §4.2)
BIDI_OVERRIDE = {
    "‪",  # LRE
    "‫",  # RLE
    "‬",  # PDF
    "‭",  # LRO
    "‮",  # RLO
    "⁦",  # LRI
    "⁧",  # RLI
    "⁨",  # FSI
    "⁩",  # PDI
}

INVISIBLE_CHARS = ZERO_WIDTH | BIDI_OVERRIDE

# Word-like sequence: 2+ letter characters in a row
WORD_RE = re.compile(r"[^\W\d_]{2,}", flags=re.UNICODE)


def _strip_invisible(text: str) -> tuple[str, int]:
    """Strip all invisible/bidi-override characters; return cleaned text + count."""
    stripped_count = 0
    out_chars = []
    for ch in text:
        if ch in INVISIBLE_CHARS:
            stripped_count += 1
            continue
        out_chars.append(ch)
    return "".join(out_chars), stripped_count


def _detect_mixed_script_words(text: str) -> list[dict[str, Any]]:
    """Flag words mixing ASCII letters with non-ASCII letters (homoglyph signature).

    Pure-ASCII words and pure-non-ASCII words are NOT flagged (the latter are
    legitimate non-English content). Only mixed-script words are suspect.
    """
    findings: list[dict[str, Any]] = []
    for match in WORD_RE.finditer(text):
        word = match.group(0)
        has_ascii_letter = any("A" <= ch <= "Z" or "a" <= ch <= "z" for ch in word)
        has_nonascii_letter = any(ord(ch) > 127 and ch.isalpha() for ch in word)
        if has_ascii_letter and has_nonascii_letter:
            non_ascii_chars = sorted({
                ch for ch in word if ord(ch) > 127 and ch.isalpha()
            })
            findings.append({
                "word": word,
                "offset": match.start(),
                "non_ascii_chars": non_ascii_chars,
                "non_ascii_codepoints": [f"U+{ord(c):04X}" for c in non_ascii_chars],
                "non_ascii_names": [unicodedata.name(c, "<unknown>") for c in non_ascii_chars],
            })
    return findings


def check(content: str) -> dict[str, Any]:
    """Run M14 normalization checks on content. Returns structured result.

    Status semantics:
    - 'normalized': cleaned NFC content, no findings
    - 'flagged': findings present (invisible chars stripped or mixed-script
      words detected) — caller should warn
    """
    original_length = len(content)
    normalized = unicodedata.normalize("NFC", content)
    cleaned, stripped_count = _strip_invisible(normalized)
    mixed_script = _detect_mixed_script_words(cleaned)

    findings: list[str] = []
    if stripped_count > 0:
        findings.append(
            f"M14: stripped {stripped_count} invisible/bidi-override character(s) "
            f"(zero-width or bidi-override); flag for review."
        )
    if mixed_script:
        findings.append(
            f"M14: {len(mixed_script)} mixed-script word(s) detected — potential "
            f"homoglyph attack (Cyrillic/Greek/etc. characters mixed into "
            f"otherwise-Latin identifiers)."
        )

    return {
        "status": "flagged" if findings else "normalized",
        "original_length": original_length,
        "normalized_length": len(cleaned),
        "stripped_count": stripped_count,
        "flagged_tokens": mixed_script,
        "findings": findings,
        "normalized_content": cleaned,
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m14_unicode_normalize")
    parser.add_argument("--content", help="Path to content file (default: stdin)")
    parser.add_argument(
        "--print-normalized",
        action="store_true",
        help="Print normalized content to stdout instead of JSON result",
    )
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = check(text)
    if args.print_normalized:
        sys.stdout.write(result["normalized_content"])
        return 0
    # Drop the full content from the JSON report to keep stdout manageable
    result_summary = {k: v for k, v in result.items() if k != "normalized_content"}
    print(json.dumps(result_summary, indent=2))
    return 0 if result["status"] == "normalized" else 1


if __name__ == "__main__":
    sys.exit(_cli())
