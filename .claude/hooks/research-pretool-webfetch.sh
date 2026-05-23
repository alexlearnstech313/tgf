#!/usr/bin/env bash
# research-pretool-webfetch.sh
# PreToolUse hook on WebFetch — URL allow-list check (M15).
# Blocks WebFetch calls to URLs not in .tgf/state/source-registry.json.
# On approval, writes pretool context to .tgf/state/pretool-context/{session_id}.json
# for PostToolUse to consume.
#
# Registered in .claude/settings.json under hooks.PreToolUse with matcher "WebFetch".
# Implementation: lib/hook_research_pretool_webfetch.py
#
# Per docs/RESEARCH-SECURITY.md §5.1 and impl plan §5.1.

set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HOOK_DIR"

exec python3 -m lib.hook_research_pretool_webfetch
