"""M3 — Schema validation of fetched content.

Validates fetched content against a per-source-type schema loaded from
.tgf/state/source-schemas/{schema_id}.json. Catches obvious tampering and
wrong-URL fetches.

Schema format (JSON):
    {
      "name": "owasp-asvs-chapter",
      "version": 1,
      "checks": {
        "min_size_bytes": <int>,
        "required_h2_pattern": <regex>,
        "required_h2_count_min": <int>,
        "required_subrule_pattern": <regex>,
        "required_subrule_count_min": <int>,
        "required_strings": [<exact string>, ...],
        "forbidden_patterns": [<regex>, ...]
      }
    }

Any check field may be omitted. Missing schema file → status='skipped'.

CLI:
    python3 -m lib.m3_schema_validate --content <file> --schema-id <schema_name>
    python3 -m lib.m3_schema_validate --content <file> --schema-file <path>

Per docs/RESEARCH-SECURITY.md §4.2 M3 and impl plan §6.1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from . import common


SCHEMAS_DIR = "source-schemas"


def _load_schema(schema_id: str) -> dict[str, Any] | None:
    """Load schema by id from .tgf/state/source-schemas/{schema_id}.json."""
    path = common.state_path(SCHEMAS_DIR, f"{schema_id}.json")
    return common.load_json(path, default=None)


def _load_schema_file(path: Path) -> dict[str, Any] | None:
    return common.load_json(path, default=None)


def check(content: str, schema: dict[str, Any] | None) -> dict[str, Any]:
    """Validate content against schema. Schema=None → status='skipped'."""
    if schema is None:
        return {
            "status": "skipped",
            "schema_name": None,
            "findings": [],
            "reason": "no schema configured for this source",
        }

    checks = schema.get("checks", {})
    findings: list[str] = []

    size = len(content.encode("utf-8"))
    min_size = checks.get("min_size_bytes")
    if isinstance(min_size, int) and size < min_size:
        findings.append(
            f"M3: content size {size} bytes is below minimum {min_size} for "
            f"schema '{schema.get('name', '<unnamed>')}' — possible truncation, "
            f"wrong-URL fetch, or upstream error response."
        )

    h2_pat = checks.get("required_h2_pattern")
    h2_min = checks.get("required_h2_count_min", 1)
    if h2_pat:
        h2_matches = re.findall(h2_pat, content, flags=re.MULTILINE)
        if len(h2_matches) < h2_min:
            findings.append(
                f"M3: required H2 pattern matched {len(h2_matches)} time(s); "
                f"expected at least {h2_min} for schema '{schema.get('name')}'. "
                f"Pattern: {h2_pat}"
            )

    subrule_pat = checks.get("required_subrule_pattern")
    subrule_min = checks.get("required_subrule_count_min", 1)
    if subrule_pat:
        subrule_matches = re.findall(subrule_pat, content, flags=re.MULTILINE)
        if len(subrule_matches) < subrule_min:
            findings.append(
                f"M3: required sub-rule pattern matched {len(subrule_matches)} "
                f"time(s); expected at least {subrule_min} for schema "
                f"'{schema.get('name')}'. Pattern: {subrule_pat}"
            )

    required = checks.get("required_strings", [])
    for s in required:
        if s not in content:
            findings.append(
                f"M3: required string not found in content for schema "
                f"'{schema.get('name')}': {s!r}"
            )

    forbidden = checks.get("forbidden_patterns", [])
    for pat in forbidden:
        if re.search(pat, content):
            findings.append(
                f"M3: forbidden pattern matched for schema "
                f"'{schema.get('name')}': {pat}"
            )

    status = "pass" if not findings else "fail"
    return {
        "status": status,
        "schema_name": schema.get("name"),
        "size_bytes": size,
        "findings": findings,
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m3_schema_validate")
    parser.add_argument("--content", help="Path to content file (default: stdin)")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--schema-id", help="Schema name (loads .tgf/state/source-schemas/<id>.json)")
    g.add_argument("--schema-file", help="Path to schema JSON file")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if args.schema_file:
        schema = _load_schema_file(Path(args.schema_file))
    elif args.schema_id:
        schema = _load_schema(args.schema_id)
    else:
        schema = None

    result = check(text, schema)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("pass", "skipped") else 1


if __name__ == "__main__":
    sys.exit(_cli())
