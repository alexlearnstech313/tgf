#!/usr/bin/env bash
# research-session-start.sh
# SessionStart hook — verifies .tgf/state/ infrastructure and injects
# research-security context into the AI session. Cannot block.
#
# Registered in .claude/settings.json under hooks.SessionStart.
# Implementation: lib/hook_research_session_start.py
#
# Per docs/RESEARCH-SECURITY.md §5.1 and impl plan §5.5.

set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HOOK_DIR"

exec python3 -m lib.hook_research_session_start
