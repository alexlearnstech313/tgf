#!/usr/bin/env bash
# research-posttool-webfetch.sh
# PostToolUse hook on WebFetch — runs all 7 M-helpers (M3, M4, M11, M13,
# M14, M18, M19) against fetched content, writes a research-log entry, and
# emits additionalContext warnings on findings.
#
# Cannot block. The block happens at PreToolUse-Write (Stage 4) when the AI
# tries to cite a flagged source.
#
# Registered in .claude/settings.json under hooks.PostToolUse with matcher "WebFetch".
# Implementation: lib/hook_research_posttool_webfetch.py
#
# Per docs/RESEARCH-SECURITY.md §5.1 / §7.1 and impl plan §5.2.

set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HOOK_DIR"

exec python3 -m lib.hook_research_posttool_webfetch
