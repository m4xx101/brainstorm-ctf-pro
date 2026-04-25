#!/usr/bin/env bash
# ⬡ FISSURE — Standalone Update Script
# bash scripts/fissure-update.sh
#
# Can be run directly, used in cronjobs, or called by Hermes cron.
# Auto-stashes local changes, pulls latest code, reinstalls deps.

set -euo pipefail

FISSURE_DIR="${HOME}/.hermes/skills/red-teaming/fissure"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

log()  { echo -e "${GREEN}✓${NC} $1"; }
info() { echo -e "${CYAN}→${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }

echo ""
echo -e "${CYAN}${BOLD}  ⬡ FISSURE — Update${NC}"
echo ""

if [ ! -d "$FISSURE_DIR/.git" ]; then
    err "Fissure not found at $FISSURE_DIR"
    echo "  Install first: curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash"
    exit 1
fi

cd "$FISSURE_DIR"

# Determine Python
PYTHON="python3"
if [ -f /proc/version ] && grep -qi microsoft /proc/version 2>/dev/null && command -v python3.exe &>/dev/null; then
    PYTHON="python3.exe"
fi

# Stash local changes
HAS_LOCAL=false
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
    HAS_LOCAL=true
    STASH_NAME="fissure-update-$(date -u +%Y%m%d-%H%M%S)"
    info "Local changes detected — stashing..."
    git stash push --include-untracked -m "$STASH_NAME" 2>/dev/null || true
fi

# Fetch
info "Fetching updates..."
if ! git fetch origin 2>/dev/null; then
    err "Failed to fetch. Check network."
    exit 1
fi

NEW_COMMITS=$(git rev-list HEAD..origin/main --count 2>/dev/null || echo "0")

if [ "$NEW_COMMITS" -eq 0 ] 2>/dev/null; then
    log "Already up to date!"
    if [ -d "venv" ]; then
        # Still reinstall deps for safety
        $PYTHON -m pip install -e . --quiet 2>/dev/null || true
    fi
    if $HAS_LOCAL; then
        info "Restoring local changes..."
        git stash pop 2>/dev/null || true
    fi
    exit 0
fi

info "Found $NEW_COMMITS new commit(s)"
info "Pulling latest..."

if ! git pull --ff-only origin main 2>/dev/null; then
    warn "Fast-forward failed — resetting to match remote..."
    git reset --hard origin/main
fi

log "Code updated!"

# Reinstall deps
if [ -f "pyproject.toml" ]; then
    info "Updating Python dependencies..."
    $PYTHON -m pip install -e . --quiet 2>/dev/null || $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || true
elif [ -f "requirements.txt" ]; then
    info "Updating Python dependencies..."
    $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || true
fi

# Bootstrap wiki
$PYTHON scripts/wiki.py bootstrap 2>/dev/null || true

# Restore stash
if $HAS_LOCAL; then
    if [ -t 0 ] && [ -t 1 ]; then
        info "Restoring local changes..."
        git stash pop 2>/dev/null || warn "Stash restore failed. Changes preserved: git stash list"
    else
        info "Local changes stashed (non-interactive mode)."
        info "  Restore: cd $FISSURE_DIR && git stash pop"
    fi
fi

echo ""
log "⬡ FISSURE updated to latest!"
echo ""
