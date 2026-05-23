#!/usr/bin/env bash
# research-pretool-write.sh
# PreToolUse hook on Write/Edit/MultiEdit — Stage 4 §2-Sources traceability
# enforcement.
#
# Blocks any write to a markdown file under skills/** when its post-edit
# content cites a source that lacks a 'verified' research-log entry in the
# current session. This is the framework's structural enforcement of the
# discipline that commit 4/12 surfaced manually.
#
# Registered in .claude/settings.json under hooks.PreToolUse with matcher
# "Write|Edit|MultiEdit". Implementation: lib/hook_research_pretool_write.py
#
# Per docs/RESEARCH-SECURITY.md §5.1 / §7.4 and impl plan §5.3.

set -euo pipefail

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HOOK_DIR"

exec python3 -m lib.hook_research_pretool_write
