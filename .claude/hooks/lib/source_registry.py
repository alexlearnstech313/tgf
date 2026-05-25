"""Source registry library: load, URL lookup, M12 independence check, and safe add.

Reads .tgf/state/source-registry.json and .tgf/state/source-org-mapping.json.
Hooks call read-only paths to decide whether a URL is approved (M15 allow-list)
and whether two source IDs are independent (M12). The ``add_source`` helper is
the only sanctioned write path — it routes through ``common.save_json`` so the
file stays UTF-8 (em-dashes preserved, no ``\\uXXXX`` escape noise).

Importable and CLI-runnable for testing:

    python3 -m lib.source_registry --lookup-url https://...
    python3 -m lib.source_registry --get-source OWASP-ASVS-V1
    python3 -m lib.source_registry --independence OWASP-ASVS-V1 NIST-SP-800-57
    python3 -m lib.source_registry --add-source CLAUDE-CODE-DOCS \\
        --tier 1 --type vendor-doc --publisher Anthropic \\
        --jurisdiction vendor --primary-url https://code.claude.com/docs/en/sub-agents \\
        --allow-pattern 'https://code.claude.com/docs/en/*' \\
        --expected-schema vendor-doc --note 'Claude Code official docs'

Programmatic registry writes MUST go through ``add_source`` (or ``common.save_json``
directly). Ad-hoc ``json.dump``/``json.dumps`` with library defaults coerces
non-ASCII to ``\\uXXXX`` escapes and corrupts the working tree on every fetch.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from typing import Any

from . import common


REGISTRY_FILE = "source-registry.json"
ORG_MAPPING_FILE = "source-org-mapping.json"


def load_registry() -> dict[str, Any]:
    """Load source-registry.json. Returns {'version': 1, 'sources': {}} if missing."""
    path = common.state_path(REGISTRY_FILE)
    return common.load_json(path, default={"version": 1, "sources": {}})


def load_org_mapping() -> dict[str, Any]:
    """Load source-org-mapping.json. Returns empty default if missing."""
    path = common.state_path(ORG_MAPPING_FILE)
    return common.load_json(path, default={"version": 1, "orgs": {}, "independence_rules": {}})


def lookup_url(url: str) -> str | None:
    """Match a URL against every source's allow_url_patterns. Returns source_id or None.

    Matches the FIRST source whose allow_url_patterns contains a glob that
    matches the URL. If no source matches, returns None — the caller (typically
    research-pretool-webfetch.sh) blocks the fetch.

    URL matching uses fnmatch.fnmatchcase (case-sensitive, ``*`` matches any
    character including ``/``).
    """
    if not url:
        return None
    registry = load_registry()
    for source_id, meta in registry.get("sources", {}).items():
        patterns = meta.get("allow_url_patterns", [])
        if not patterns and meta.get("primary_url") == url:
            return source_id
        for pattern in patterns:
            if fnmatch.fnmatchcase(url, pattern):
                return source_id
    return None


def get_source(source_id: str) -> dict[str, Any] | None:
    """Return source metadata dict or None if not present."""
    registry = load_registry()
    return registry.get("sources", {}).get(source_id)


def get_org(source_id: str) -> str | None:
    """Return the publishing organization for a source_id, or None."""
    meta = get_source(source_id)
    if not meta:
        return None
    return meta.get("publisher")


def independence_check(source_id_a: str, source_id_b: str) -> bool:
    """M12: two sources are independent only if their publishing orgs differ.

    Same source ID against itself is never independent. Same-org sources
    (e.g., OWASP-ASVS-V1 vs OWASP-CHEAT-PS, both OWASP) are not independent.
    Cross-org sources (OWASP vs NIST, IETF vs ISO) are independent.

    Returns False if either source is unknown — caller treats unknown as
    failed independence (conservative default).
    """
    if source_id_a == source_id_b:
        return False
    org_a = get_org(source_id_a)
    org_b = get_org(source_id_b)
    if not org_a or not org_b:
        return False
    return org_a != org_b


def list_sources(tier: int | None = None) -> list[str]:
    """List source IDs, optionally filtered by tier (1/2/3)."""
    registry = load_registry()
    out = []
    for source_id, meta in registry.get("sources", {}).items():
        if tier is None or meta.get("tier") == tier:
            out.append(source_id)
    return sorted(out)


REQUIRED_FIELDS = ("tier", "type", "publisher", "primary_url")
VALID_TIERS = (1, 2, 3)
KNOWN_FIELDS = (
    "tier", "type", "publisher", "jurisdiction", "primary_url",
    "allow_url_patterns", "expected_schema", "pinned", "last_verified",
    "note", "cited_in", "id_prefix_match",
)


def add_source(source_id: str, metadata: dict[str, Any], force: bool = False) -> dict[str, Any]:
    """Add (or overwrite with ``force=True``) a source entry, persisting via common.save_json.

    Validates required fields and tier range, normalizes defaults so every entry
    has the same shape, then writes the whole registry back with UTF-8 preserved.
    Unknown fields pass through (id_prefix_match etc. are accepted as-is).

    Raises ValueError on duplicate id (without force), missing required fields,
    invalid tier, or wrong-typed allow_url_patterns / cited_in.
    """
    if not source_id or not isinstance(source_id, str):
        raise ValueError("source_id must be a non-empty string")

    registry = load_registry()
    sources = registry.setdefault("sources", {})
    if source_id in sources and not force:
        raise ValueError(f"Source {source_id!r} already exists. Pass force=True to overwrite.")

    missing = [k for k in REQUIRED_FIELDS if k not in metadata]
    if missing:
        raise ValueError(f"Missing required fields for {source_id!r}: {missing}")
    if metadata["tier"] not in VALID_TIERS:
        raise ValueError(f"tier must be one of {VALID_TIERS} (got {metadata['tier']!r})")

    patterns = metadata.get("allow_url_patterns", [])
    if not isinstance(patterns, list) or not all(isinstance(p, str) for p in patterns):
        raise ValueError("allow_url_patterns must be a list of strings")
    cited_in = metadata.get("cited_in", [])
    if not isinstance(cited_in, list) or not all(isinstance(c, str) for c in cited_in):
        raise ValueError("cited_in must be a list of strings")

    entry: dict[str, Any] = {
        "tier": metadata["tier"],
        "type": metadata["type"],
        "publisher": metadata["publisher"],
        "jurisdiction": metadata.get("jurisdiction"),
        "primary_url": metadata["primary_url"],
        "allow_url_patterns": list(patterns),
        "expected_schema": metadata.get("expected_schema"),
        "pinned": bool(metadata.get("pinned", False)),
        "last_verified": metadata.get("last_verified"),
        "note": metadata.get("note", ""),
        "cited_in": list(cited_in),
    }
    for k, v in metadata.items():
        if k not in entry:
            entry[k] = v

    sources[source_id] = entry
    common.save_json(common.state_path(REGISTRY_FILE), registry)
    return entry


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="source_registry")
    parser.add_argument("--lookup-url", metavar="URL", help="Match URL against registry")
    parser.add_argument("--get-source", metavar="SOURCE_ID", help="Print source metadata")
    parser.add_argument(
        "--independence",
        nargs=2,
        metavar=("SOURCE_A", "SOURCE_B"),
        help="M12 independence check between two source IDs",
    )
    parser.add_argument("--list", action="store_true", help="List all source IDs")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3],
                        help="Filter --list by tier OR tier for --add-source")

    parser.add_argument("--add-source", metavar="SOURCE_ID",
                        help="Add a new source entry, persisted via common.save_json")
    parser.add_argument("--type", help="Source type (e.g. owasp-cheat-sheet, nist-sp, vendor-doc)")
    parser.add_argument("--publisher", help="Publishing organization (e.g. OWASP, NIST, Anthropic)")
    parser.add_argument("--jurisdiction", help="Source jurisdiction (US-federal, international, vendor, ...)")
    parser.add_argument("--primary-url", dest="primary_url",
                        help="Canonical URL for the source")
    parser.add_argument("--allow-pattern", dest="allow_patterns", action="append", default=[],
                        metavar="GLOB", help="M15 allow-list glob (repeatable)")
    parser.add_argument("--expected-schema", dest="expected_schema",
                        help="Schema id for M3 validation (matches source-schemas/<id>.json)")
    parser.add_argument("--note", default="", help="Free-form note for the entry")
    parser.add_argument("--cited-in", dest="cited_in", action="append", default=[],
                        metavar="REF", help="Citing artifact path or id (repeatable)")
    parser.add_argument("--id-prefix-match", dest="id_prefix_match", action="append", default=[],
                        metavar="PREFIX", help="Citation alias prefix (repeatable)")
    parser.add_argument("--pinned", action="store_true", help="Mark source as pinned")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing entry when used with --add-source")

    args = parser.parse_args()

    if args.lookup_url:
        result = lookup_url(args.lookup_url)
        print(json.dumps({"url": args.lookup_url, "source_id": result}))
        return 0 if result else 1

    if args.get_source:
        meta = get_source(args.get_source)
        print(json.dumps(meta, indent=2) if meta else json.dumps(None))
        return 0 if meta else 1

    if args.independence:
        result = independence_check(*args.independence)
        print(json.dumps({"sources": args.independence, "independent": result}))
        return 0

    if args.list:
        for sid in list_sources(args.tier):
            print(sid)
        return 0

    if args.add_source:
        if args.tier is None or not args.type or not args.publisher or not args.primary_url:
            parser.error("--add-source requires --tier, --type, --publisher, --primary-url")
        metadata: dict[str, Any] = {
            "tier": args.tier,
            "type": args.type,
            "publisher": args.publisher,
            "primary_url": args.primary_url,
            "allow_url_patterns": args.allow_patterns,
            "note": args.note,
            "cited_in": args.cited_in,
            "pinned": args.pinned,
        }
        if args.jurisdiction:
            metadata["jurisdiction"] = args.jurisdiction
        if args.expected_schema:
            metadata["expected_schema"] = args.expected_schema
        if args.id_prefix_match:
            metadata["id_prefix_match"] = args.id_prefix_match
        try:
            entry = add_source(args.add_source, metadata, force=args.force)
        except ValueError as err:
            print(f"error: {err}", file=sys.stderr)
            return 2
        print(json.dumps({"added": args.add_source, "entry": entry}, indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
