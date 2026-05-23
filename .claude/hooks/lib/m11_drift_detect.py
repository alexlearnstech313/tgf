"""M11 — Content-drift detection against baseline.

Diffs fetched content against the previously verified baseline at
.tgf/state/source-baselines/{source_id}.md (or arbitrary baseline file).
Surfaces structural changes (citation tables, parameter values, section
structure) at higher severity than prose-only changes.

CLI:
    python3 -m lib.m11_drift_detect --content <file> --baseline <baseline_file>
    python3 -m lib.m11_drift_detect --content <file> --source-id <id>

Output JSON: {status, summary, lines_changed, structural_changes,
diff_excerpt}.

Per docs/RESEARCH-SECURITY.md §4.3 M11 and impl plan §6.3.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from typing import Any

from . import common


BASELINES_DIR = "source-baselines"


# Lines that indicate structural / high-severity content
STRUCTURAL_PATTERNS = [
    re.compile(r"^\s*\|.*\|.*\|"),                                          # markdown table rows
    re.compile(r"^\s*#{1,6}\s"),                                            # markdown headings
    re.compile(r"^\s*\*\*V\d+\.\d+\.\d+\*\*"),                              # ASVS sub-rule IDs
    re.compile(r"\b(?:Argon2id|bcrypt|scrypt|PBKDF2|AES|RSA|SHA)\b",       # crypto algorithm names
               re.IGNORECASE),
    re.compile(r"\b\d{4,}\s*(?:iterations?|rounds?|bits?)\b", re.IGNORECASE),  # parameter values
    re.compile(r"^\s*-\s+\*\*[^*]+\*\*\s*[—:-]"),                          # AP/CP list items
]


def _is_structural(line: str) -> bool:
    return any(pat.search(line) for pat in STRUCTURAL_PATTERNS)


def check(content: str, baseline: str | None) -> dict[str, Any]:
    """Diff content against baseline. None baseline → status='no_baseline'."""
    if baseline is None:
        return {
            "status": "no_baseline",
            "summary": "no baseline on file — first fetch establishes baseline",
            "lines_changed": 0,
            "structural_changes": 0,
            "diff_excerpt": "",
        }

    if baseline == content:
        return {
            "status": "pass",
            "summary": "content identical to baseline",
            "lines_changed": 0,
            "structural_changes": 0,
            "diff_excerpt": "",
        }

    baseline_lines = baseline.splitlines(keepends=True)
    content_lines = content.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        baseline_lines,
        content_lines,
        fromfile="baseline",
        tofile="current",
        n=2,
    ))

    lines_changed = 0
    structural_changes = 0
    for line in diff:
        if line.startswith("+") and not line.startswith("+++"):
            lines_changed += 1
            if _is_structural(line[1:]):
                structural_changes += 1
        elif line.startswith("-") and not line.startswith("---"):
            lines_changed += 1
            if _is_structural(line[1:]):
                structural_changes += 1

    if structural_changes > 0:
        status = "drift_high"
        summary = (
            f"M11: {structural_changes} structural change(s) detected — "
            f"affects citation tables, headings, sub-rule IDs, or "
            f"parameter values. Total {lines_changed} line(s) changed."
        )
    elif lines_changed > 0:
        status = "drift_low"
        summary = (
            f"M11: {lines_changed} prose-only line(s) changed; no "
            f"structural changes detected."
        )
    else:
        status = "pass"
        summary = "no diff detected"

    diff_excerpt = "".join(diff[:200])
    return {
        "status": status,
        "summary": summary,
        "lines_changed": lines_changed,
        "structural_changes": structural_changes,
        "diff_excerpt": diff_excerpt,
    }


def _load_baseline_by_source_id(source_id: str) -> str | None:
    path = common.state_path(BASELINES_DIR, f"{source_id}.md")
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m11_drift_detect")
    parser.add_argument("--content", help="Path to current content file (default: stdin)")
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--baseline", help="Path to baseline file")
    g.add_argument("--source-id", help="Source ID to lookup baseline in .tgf/state/source-baselines/")
    args = parser.parse_args()

    if args.content:
        with open(args.content, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    baseline: str | None
    if args.baseline:
        with open(args.baseline, "r", encoding="utf-8") as f:
            baseline = f.read()
    elif args.source_id:
        baseline = _load_baseline_by_source_id(args.source_id)
    else:
        baseline = None

    result = check(text, baseline)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("pass", "no_baseline", "drift_low") else 1


if __name__ == "__main__":
    sys.exit(_cli())
