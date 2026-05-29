#!/usr/bin/env python3
"""GFM anchor-slug linter — catches dead in-repo Markdown anchor references.

Background (WS5 / WP3): the WS4 retroactive audit found that every Phase 5
skill, and several Phase 6 skills, advertise cross-reference anchors of the
form ``file.md#some-slug`` whose slug was hand-authored and drifts from the
slug GitHub actually generates for the target heading. The drift shows up
wherever a heading carries punctuation — commas, parentheses, ``+``, slashes,
em-dashes — or where the author dropped a word. A reader who follows the
advertised anchor lands at the top of the file instead of the heading.

This linter is deterministic: it reimplements GitHub's slug algorithm
(github-slugger equivalent), computes the real slug for every heading, then
checks every ``file.md#frag`` reference (and same-file ``](#frag)`` link
target) against the target file's real heading slugs. It reports only
references whose *target file exists in the repo* but whose fragment does not
resolve — so external URLs and out-of-scope files never produce noise.

Reusable beyond WS5: a CI candidate. Exit code is non-zero when mismatches are
found so it can gate a pipeline.

Usage:
    python3 scripts/gfm_anchor_lint.py                  # lint default scope
    python3 scripts/gfm_anchor_lint.py skills/ docs/    # lint given paths
    python3 scripts/gfm_anchor_lint.py --json           # machine-readable
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from typing import Dict, List, Optional, Tuple

# Default lint scope when no paths are given on the command line: every skill
# Markdown file plus the docs/ tree. Root governance docs are added explicitly
# because they carry cross-references too.
DEFAULT_PATHS = ["skills", "docs"]
DEFAULT_ROOT_DOCS = [
    "CLAUDE.md", "ROADMAP.md", "DECISIONS.md", "README.md",
    "CHANGELOG.md", "ERROR-LOG.md",
]

# A fenced code block opens with >=3 backticks or tildes (<=3 leading spaces),
# optionally followed by an info string. Per CommonMark, the CLOSING fence must
# use the same character, be at least as long, and carry NO info string — so a
# line like ```` ```typescript ```` can only ever OPEN a block, never close one.
# Getting this right matters: skill examples sometimes show a fenced block whose
# content is itself Markdown containing ```` ```lang ```` lines, and a naive
# "every fence line toggles" parser desyncs and swallows real headings.
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})([^`]*)$")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
# A reference that names a target file and a fragment: `rules.md#rule-51-...`.
# Matches inside code spans, link targets, or bare prose alike.
FILE_FRAG_RE = re.compile(r"([A-Za-z0-9._\-/]+\.md)#([A-Za-z0-9_\-]+)")
# A same-file link target: `](#some-anchor)`.
SAME_FILE_RE = re.compile(r"\]\(#([A-Za-z0-9_\-]+)\)")
# Markdown link `[text](url)` -> keep only the visible text when slugging a heading.
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slugify(text: str) -> str:
    """Reimplements github-slugger: lowercase, drop everything that is not a
    Unicode letter/number/mark (underscore and hyphen are kept), and turn each
    ASCII space into a hyphen. No hyphen-collapsing and no edge-trimming — this
    matches GitHub, so ``A + B`` becomes ``a--b`` (the ``+`` is dropped, leaving
    the two flanking spaces as two hyphens)."""
    s = text.strip().lower()
    out: List[str] = []
    for ch in s:
        if ch == " ":
            out.append("-")
        elif ch in "-_":
            out.append(ch)
        else:
            if unicodedata.category(ch)[0] in ("L", "N", "M"):
                out.append(ch)
            # anything else (punctuation, symbols, other whitespace) is dropped
    return "".join(out)


def heading_text(raw: str) -> str:
    """Strip Markdown link syntax from a heading so the URL never leaks into the
    slug. Backticks/emphasis need no special handling — the slug algorithm drops
    those characters while keeping the inner text."""
    return MD_LINK_RE.sub(r"\1", raw)


def content_lines(lines: List[str]):
    """Yield (lineno, line) for lines OUTSIDE fenced code blocks, applying
    CommonMark fence rules: a closing fence uses the same fence character, is at
    least as long as the opener, and carries no info string. Fence lines
    themselves are never yielded."""
    in_fence = False
    fence_char = ""
    fence_len = 0
    for lineno, line in enumerate(lines, start=1):
        m = FENCE_OPEN_RE.match(line)
        if not in_fence:
            if m:
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                in_fence = True
                continue
            yield lineno, line
        else:
            if (m and m.group(1)[0] == fence_char
                    and len(m.group(1)) >= fence_len
                    and m.group(2).strip() == ""):
                in_fence = False
            # closer or content: a fence-region line is never content


def file_heading_slugs(path: str) -> List[str]:
    """Return the ordered list of heading slugs for a file, applying
    github-slugger's duplicate disambiguation (second `foo` -> `foo-1`)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []

    slugs: List[str] = []
    seen: Dict[str, int] = {}
    for _lineno, line in content_lines(lines):
        m = HEADING_RE.match(line)
        if not m:
            continue
        base = slugify(heading_text(m.group(2)))
        if not base:
            continue
        if base in seen:
            seen[base] += 1
            slug = f"{base}-{seen[base]}"
        else:
            seen[base] = 0
            slug = base
        slugs.append(slug)
    return slugs


# Cache of computed slug sets, keyed by absolute path.
_slug_cache: Dict[str, List[str]] = {}


def slugs_for(abspath: str) -> Optional[List[str]]:
    if not os.path.isfile(abspath):
        return None
    if abspath not in _slug_cache:
        _slug_cache[abspath] = file_heading_slugs(abspath)
    return _slug_cache[abspath]


def suggest(frag: str, candidates: List[str]) -> Optional[str]:
    """Best-guess correct slug: the candidate sharing the longest common prefix
    with the broken fragment, provided they at least share a leading token."""
    best, best_len = None, 0
    for cand in candidates:
        n = 0
        for a, b in zip(frag, cand):
            if a != b:
                break
            n += 1
        if n > best_len:
            best, best_len = cand, n
    # require sharing at least up to the first hyphen group (e.g. "rule-54", "ap-4")
    head = frag.split("-")[0]
    if best and best_len >= len(head):
        return best
    return None


def lint_file(path: str) -> List[dict]:
    """Return a list of mismatch records for one referencing file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return []

    findings: List[dict] = []
    base_dir = os.path.dirname(os.path.abspath(path))
    own = slugs_for(os.path.abspath(path)) or []
    for lineno, line in content_lines(lines):
        # cross-file references: file.md#frag
        for m in FILE_FRAG_RE.finditer(line):
            file_ref, frag = m.group(1), m.group(2)
            target = os.path.normpath(os.path.join(base_dir, file_ref))
            cand = slugs_for(target)
            if cand is None:
                # target file not in repo (external URL, out-of-scope) -> skip
                continue
            if frag not in cand:
                findings.append({
                    "file": path,
                    "line": lineno,
                    "ref": f"{file_ref}#{frag}",
                    "target": os.path.relpath(target),
                    "suggest": suggest(frag, cand),
                })

        # same-file references: ](#frag)
        for m in SAME_FILE_RE.finditer(line):
            frag = m.group(1)
            if frag not in own:
                findings.append({
                    "file": path,
                    "line": lineno,
                    "ref": f"#{frag}",
                    "target": path,
                    "suggest": suggest(frag, own),
                })
    return findings


def collect_md_files(paths: List[str]) -> List[str]:
    out: List[str] = []
    for p in paths:
        if os.path.isfile(p) and p.endswith(".md"):
            out.append(p)
        elif os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                if "/.git" in root:
                    continue
                for fn in sorted(files):
                    if fn.endswith(".md"):
                        out.append(os.path.join(root, fn))
    return sorted(set(out))


def _cli() -> int:
    ap = argparse.ArgumentParser(prog="gfm_anchor_lint")
    ap.add_argument("paths", nargs="*", help="files or dirs to lint (default: skills docs + root governance docs)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if args.paths:
        targets = collect_md_files(args.paths)
    else:
        targets = collect_md_files(DEFAULT_PATHS)
        targets += [d for d in DEFAULT_ROOT_DOCS if os.path.isfile(d)]
        targets = sorted(set(targets))

    all_findings: List[dict] = []
    for f in targets:
        all_findings.extend(lint_file(f))

    if args.json:
        print(json.dumps({
            "files_linted": len(targets),
            "mismatches": len(all_findings),
            "findings": all_findings,
        }, indent=2))
    else:
        if not all_findings:
            print(f"OK — {len(targets)} files linted, 0 dead anchors.")
        else:
            by_file: Dict[str, List[dict]] = {}
            for fnd in all_findings:
                by_file.setdefault(fnd["file"], []).append(fnd)
            for fpath in sorted(by_file):
                print(f"\n{fpath}")
                for fnd in by_file[fpath]:
                    sug = f"  →  {fnd['target']}#{fnd['suggest']}" if fnd["suggest"] else "  (no suggestion)"
                    print(f"  L{fnd['line']}: {fnd['ref']}{sug}")
            print(f"\n{len(all_findings)} dead anchor(s) across {len(by_file)} file(s); {len(targets)} files linted.")

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(_cli())
