#!/usr/bin/env bash
# research-stop.sh
# Stop hook — Stage 5→6 gate. Refuses to end the response if any cited source
# lacks 'verified' research-log status this session, or if any control-locking
# skill change (rules.md / anti-patterns.md / SKILL.md under skills/security-*/)
# lacks an M8 approval artifact.
#
# Handles stop_hook_active reentrancy correctly (passes through to avoid loops).
#
# Registered in .claude/settings.json under hooks.Stop.
# Implementation: lib/hook_research_stop.py
#
# Per docs/RESEARCH-SECURITY.md §5.4 / §7.6 and impl plan §5.4.

set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HOOK_DIR"

exec python3 -m lib.hook_research_stop
