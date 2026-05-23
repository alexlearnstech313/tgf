"""Citation parser — extract source IDs from skill markdown files.

Pulls source IDs from two locations:

1. §2 Authoritative Sources table (first column of each markdown table row)
2. Inline citations in body text (anything matching a known source-ID prefix)

Resolves variants like 'CWE-79' to canonical 'MITRE-CWE' and 'OWASP-TOP10-A04'
to 'OWASP-TOP10-2025' using each registered source's id_prefix_match field.

Used by PreToolUse-Write hook (Step 11) to verify every citation in a skill
file has a verified research-log entry before allowing the write.

CLI:
    python3 -m lib.citation_parser --file <path>
    cat skill.md | python3 -m lib.citation_parser
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from . import source_registry


# Tokens that look like authoritative-source citation IDs. Must start with a
# known prefix from a known authoritative-source family, followed by a hyphen
# and at least one alphanumeric segment. The registry-driven resolution
# catches anything we care about; this regex is just the coarse filter.
CITATION_TOKEN_RE = re.compile(
    r"\b(?:OWASP|NIST|FIPS|RFC|CWE|MITRE|ISO|IETF)-[A-Z0-9][A-Z0-9-]*\b"
)


# Known source-id prefixes (used as a coarse filter before registry lookup)
KNOWN_PREFIXES = ("OWASP-", "NIST-", "FIPS-", "RFC-", "CWE-", "MITRE-", "ISO-", "IETF-")


def _is_candidate(token: str) -> bool:
    """True if token has a known prefix and minimum length."""
    if len(token) < 4:
        return False
    return any(token.startswith(p) for p in KNOWN_PREFIXES)


def _section_range(text: str, section_marker: str) -> tuple[int, int] | None:
    """Locate the byte range of a markdown section by H2 heading prefix.

    Section ends at the next H2 heading or EOF. Used to scope §2 Sources
    table extraction to only the §2 section.
    """
    m = re.search(rf"^##\s+{re.escape(section_marker)}", text, re.MULTILINE)
    if not m:
        return None
    start = m.start()
    next_h2 = re.search(r"^##\s+", text[m.end():], re.MULTILINE)
    end = m.end() + next_h2.start() if next_h2 else len(text)
    return start, end


def extract_sources_table(text: str) -> list[dict[str, Any]]:
    """Extract source IDs from any markdown table whose first column resembles a citation.

    Returns list of {source_id, raw_row, line_no} for inspection.
    """
    rows: list[dict[str, Any]] = []
    section = _section_range(text, "§2") or _section_range(text, "§2 Authoritative Sources")
    if section:
        body = text[section[0]:section[1]]
        base_offset = section[0]
    else:
        body = text
        base_offset = 0

    for line_match in re.finditer(r"^\|.*\|.*$", body, re.MULTILINE):
        line = line_match.group(0)
        if re.match(r"^\|[\s\-:|]+\|[\s\-:|]+\|", line):
            continue
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if not cells:
            continue
        first_cell = cells[0]
        if not _is_candidate(first_cell):
            continue
        line_no = body[:line_match.start()].count("\n") + body.count("\n", 0, 0)
        rows.append({
            "source_id": first_cell,
            "raw_row": line,
            "offset": base_offset + line_match.start(),
        })
    return rows


def extract_inline_citations(text: str) -> list[dict[str, Any]]:
    """Extract candidate citation tokens from body text (excluding code fences).

    Returns list of {token, offset}. Tokens are not deduplicated.
    """
    body = re.sub(r"```[\s\S]*?```", lambda m: " " * (m.end() - m.start()), text)
    body = re.sub(r"`[^`\n]+`", lambda m: " " * (m.end() - m.start()), body)

    tokens: list[dict[str, Any]] = []
    for match in CITATION_TOKEN_RE.finditer(body):
        tok = match.group(0)
        if _is_candidate(tok):
            tokens.append({
                "token": tok,
                "offset": match.start(),
            })
    return tokens


def resolve(citation_id: str, registry: dict[str, Any] | None = None) -> str | None:
    """Resolve a raw citation ID to a canonical registry source_id.

    Resolution order:
    1. Exact match against registry.sources keys
    2. id_prefix_match: each canonical source lists prefixes; longest match wins
    3. None if no resolution
    """
    if registry is None:
        registry = source_registry.load_registry()
    sources = registry.get("sources", {})
    if citation_id in sources:
        return citation_id

    best_match: tuple[int, str] | None = None
    for canonical_id, meta in sources.items():
        for prefix in meta.get("id_prefix_match", []):
            if citation_id.startswith(prefix):
                key = (len(prefix), canonical_id)
                if best_match is None or key > best_match:
                    best_match = key
    return best_match[1] if best_match else None


def parse(text: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    """Parse text for all citations and resolve to canonical source IDs.

    Returns:
        {
          "table_rows": [{source_id, canonical, offset}, ...],
          "inline": [{token, canonical, offset}, ...],
          "canonical_ids": [<unique sorted canonical source_ids>],
          "unresolved": [<unique unresolved raw tokens>],
        }
    """
    if registry is None:
        registry = source_registry.load_registry()

    table_rows = extract_sources_table(text)
    inline = extract_inline_citations(text)

    canonical_set: set[str] = set()
    unresolved_set: set[str] = set()

    for row in table_rows:
        canon = resolve(row["source_id"], registry)
        row["canonical"] = canon
        if canon:
            canonical_set.add(canon)
        else:
            unresolved_set.add(row["source_id"])

    for tok in inline:
        canon = resolve(tok["token"], registry)
        tok["canonical"] = canon
        if canon:
            canonical_set.add(canon)
        elif _is_candidate(tok["token"]):
            unresolved_set.add(tok["token"])

    return {
        "table_rows": table_rows,
        "inline": inline,
        "canonical_ids": sorted(canonical_set),
        "unresolved": sorted(unresolved_set),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="citation_parser")
    parser.add_argument("--file", help="Path to skill markdown file (default: stdin)")
    parser.add_argument("--summary-only", action="store_true",
                        help="Print only canonical_ids and unresolved")
    args = parser.parse_args()

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = parse(text)
    if args.summary_only:
        print(json.dumps({
            "canonical_ids": result["canonical_ids"],
            "unresolved": result["unresolved"],
        }, indent=2))
    else:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_cli())
