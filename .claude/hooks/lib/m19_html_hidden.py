"""M19 — HTML hidden-content scan.

Parses HTML and surfaces content that survived to extracted text but would
not be visible to a human reader: display:none / visibility:hidden inline
styles, zero-opacity elements, off-screen positioning, alt-text on non-image
elements, HTML comments containing suspicious content, hidden form fields
with security-relevant values.

CLI:
    python3 -m lib.m19_html_hidden --html <file>
    cat content.html | python3 -m lib.m19_html_hidden

Output JSON: {status, hidden_content: [{element, location, content_snippet, reason}]}.

Per docs/RESEARCH-SECURITY.md §4.2 M19 and impl plan §6.7. Requires lxml
(implementation plan §2 prerequisite).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


try:
    from lxml import html as lxml_html
    from lxml import etree as lxml_etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False


HIDE_STYLE_RE = re.compile(
    r"(?:display\s*:\s*none|visibility\s*:\s*hidden|opacity\s*:\s*0(?:\.0+)?\b)",
    re.IGNORECASE,
)
OFFSCREEN_STYLE_RE = re.compile(
    r"(?:left\s*:\s*-\d{4,}|top\s*:\s*-\d{4,}|text-indent\s*:\s*-\d{4,})",
    re.IGNORECASE,
)
SUSPICIOUS_COMMENT_RE = re.compile(
    r"(?:ignore|disregard|system\s*:|assistant\s*:|new\s+instruction|you\s+are\s+now)",
    re.IGNORECASE,
)


def _is_hidden(element: Any) -> tuple[bool, str | None]:
    """Return (is_hidden, reason) for an element based on inline style/hidden attrs."""
    style = (element.get("style") or "").strip()
    if HIDE_STYLE_RE.search(style):
        return True, f"inline style hides element: {style[:120]}"
    if OFFSCREEN_STYLE_RE.search(style):
        return True, f"inline style positions off-screen: {style[:120]}"
    if element.get("hidden") is not None:
        return True, "hidden attribute present"
    aria_hidden = element.get("aria-hidden")
    if aria_hidden and aria_hidden.lower() == "true":
        return True, "aria-hidden=true"
    return False, None


def _text_with_offset(element: Any) -> str:
    text_parts: list[str] = []
    if element.text:
        text_parts.append(element.text)
    for child in element.iterchildren():
        text_parts.append(_text_with_offset(child))
        if child.tail:
            text_parts.append(child.tail)
    return "".join(text_parts).strip()


def check(html_content: str) -> dict[str, Any]:
    if not LXML_AVAILABLE:
        return {
            "status": "skipped",
            "reason": "lxml not available — install lxml to enable M19",
            "hidden_content": [],
        }

    try:
        doc = lxml_html.fromstring(html_content)
    except (lxml_etree.ParserError, ValueError) as e:
        return {
            "status": "skipped",
            "reason": f"unparseable HTML: {e}",
            "hidden_content": [],
        }

    findings: list[dict[str, Any]] = []

    for element in doc.iter():
        if not hasattr(element, "tag") or not isinstance(element.tag, str):
            continue
        hidden, reason = _is_hidden(element)
        if hidden:
            text = _text_with_offset(element)
            if text:
                findings.append({
                    "element": element.tag,
                    "reason": reason,
                    "content_snippet": text[:200],
                    "length": len(text),
                })

    for element in doc.iter():
        if not hasattr(element, "tag") or not isinstance(element.tag, str):
            continue
        alt = element.get("alt")
        if alt and element.tag.lower() not in ("img", "area", "input"):
            findings.append({
                "element": element.tag,
                "reason": "alt attribute on non-image element (M19 — content invisible to sighted readers)",
                "content_snippet": alt[:200],
                "length": len(alt),
            })

    for comment in doc.xpath("//comment()"):
        comment_text = (comment.text or "").strip()
        if SUSPICIOUS_COMMENT_RE.search(comment_text):
            findings.append({
                "element": "comment",
                "reason": "HTML comment contains injection-style phrase",
                "content_snippet": comment_text[:200],
                "length": len(comment_text),
            })

    for hidden_input in doc.xpath("//input[@type='hidden']"):
        value = hidden_input.get("value") or ""
        name = hidden_input.get("name") or ""
        if value:
            findings.append({
                "element": "input[hidden]",
                "reason": "hidden input field with value",
                "content_snippet": f"name={name!r} value={value[:120]!r}",
                "length": len(value),
            })

    status = "flagged" if findings else "pass"
    return {
        "status": status,
        "hidden_content": findings,
        "count": len(findings),
    }


def _cli() -> int:
    parser = argparse.ArgumentParser(prog="m19_html_hidden")
    parser.add_argument("--html", help="Path to HTML file (default: stdin)")
    args = parser.parse_args()

    if args.html:
        with open(args.html, "r", encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    result = check(text)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] in ("pass", "skipped") else 1


if __name__ == "__main__":
    sys.exit(_cli())
