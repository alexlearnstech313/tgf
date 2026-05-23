"""M13 — Hash pinning check for highest-stakes sources.

Compute SHA-256 of fetched content; compare to pinned hash from
.tgf/state/source-hashes.json. Used by PostToolUse-WebFetch.

CLI:
    python3 -m lib.m13_hash_check --content <file> [--pinned-hash <sha256_hex>]
    cat content | python3 -m lib.m13_hash_check --pinned-hash <sha256_hex>

When --pinned-hash is omitted, returns status='skipped' (no pinning configured
for this source yet — first fetch).

Per docs/RESEARCH-SECURITY.md §4.3 M13 and impl plan §6.4.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any


def check(content: str | bytes, pinned_hash: str | None) -> dict[str, Any]:
    """Compute SHA-256; compare to pinned hash if provided.

    Status semantics:
    - 'pass': pinned hash supplied AND matches computed hash
    - 'fail': pinned hash supplied AND mismatch (M13 violation)
    - 'skipped': no pinned hash (first-fetch or non-pinned source)
    """
    if isinstance(content, str):
        data = content.encode("utf-8")
    else:
        data = content
    computed = hashlib.sha256(data).hexdigest()

    if not pinned_hash:
        return {
            "status": "skipped",
            "computed_hash": computed,
            "pinned_hash": None,
            "finding": None,
        }

    pinned_norm = pinned_hash.strip().lower()
    if pinned_norm.startswith("sha256:"):
        pinned_norm = pinned_norm[len("sha256:"):]

    if computed == pinned_norm:
        return {
            "status": "pass",
            "computed_hash": computed,
            "pinned_hash": pinned_norm,
            "finding": None,
        }
    return {
        "status": "fail",
        "computed_hash": computed,
        "pinned_hash": pinned_norm,
        "finding": (
            "M13: content hash does not match pinned hash. Source content "
            "has changed since pinning — possible legitimate update or "
            "tampering. Requires human review before citing."
        ),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m13_hash_check")
    parser.add_argument("--content", help="Path to content file (default: stdin)")
    parser.add_argument("--pinned-hash", help="Expected SHA-256 hex (with or without sha256: prefix)")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "rb") as f:
            data = f.read()
    else:
        data = sys.stdin.buffer.read()

    result = check(data, args.pinned_hash)
    print(json.dumps(result))
    return 0 if result["status"] in ("pass", "skipped") else 1


if __name__ == "__main__":
    sys.exit(_cli())
