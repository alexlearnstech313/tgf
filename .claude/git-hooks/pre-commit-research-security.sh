#!/usr/bin/env bash
# pre-commit-research-security.sh
# Git pre-commit hook (defense in depth) — replays the Stop hook's research-
# security checks at git layer. Catches anything that slipped past in-session
# hooks: missing M8 approvals for control-locking skill changes, and skill
# citations that lack a verified research-log entry.
#
# Per docs/RESEARCH-SECURITY.md §7.6 and impl plan §5.4.
#
# INSTALLATION (one-time, per clone):
#   Option A (recommended): use this directory as core.hooksPath
#       git config core.hooksPath .claude/git-hooks
#       mv .claude/git-hooks/pre-commit-research-security.sh .claude/git-hooks/pre-commit
#       chmod +x .claude/git-hooks/pre-commit
#   Option B: symlink from .git/hooks
#       ln -sf ../../.claude/git-hooks/pre-commit-research-security.sh .git/hooks/pre-commit
#
# Bypass (emergency only, audit-logged in commit message):
#       TGF_PRECOMMIT_BYPASS="reason for bypass" git commit ...

set -euo pipefail

if [[ "${TGF_PRECOMMIT_BYPASS:-}" != "" ]]; then
    echo "[pre-commit-research-security] BYPASS active: ${TGF_PRECOMMIT_BYPASS}" >&2
    echo "[pre-commit-research-security] Recommended: record this bypass in the commit message." >&2
    exit 0
fi

HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOKS_LIB_DIR="$REPO_ROOT/.claude/hooks"

if [[ ! -d "$HOOKS_LIB_DIR/lib" ]]; then
    echo "[pre-commit-research-security] hooks lib directory not found at $HOOKS_LIB_DIR/lib" >&2
    echo "  This commit is allowed because the framework infrastructure is missing." >&2
    echo "  If you intend to run research-security checks, restore .claude/hooks/lib/." >&2
    exit 0
fi

cd "$HOOKS_LIB_DIR"
exec python3 -m lib.git_precommit_check
