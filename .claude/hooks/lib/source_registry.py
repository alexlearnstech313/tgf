"""Source registry library: load, URL lookup, and M12 independence check.

Reads .tgf/state/source-registry.json and .tgf/state/source-org-mapping.json.
Pure read-only — hooks call into this to decide whether a URL is approved
(M15 allow-list) and whether two source IDs are independent (M12).

Importable and CLI-runnable for testing:

    python3 -m lib.source_registry --lookup-url https://...
    python3 -m lib.source_registry --get-source OWASP-ASVS-V1
    python3 -m lib.source_registry --independence OWASP-ASVS-V1 NIST-SP-800-57
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
    parser.add_argument("--tier", type=int, choices=[1, 2, 3], help="Filter --list by tier")
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

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(_cli())
