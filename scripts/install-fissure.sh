#!/usr/bin/env bash
# ⬡ FISSURE — One-shot installer & updater
# curl -fsSL https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh | bash
# bash install-fissure.sh          # fresh install
# bash install-fissure.sh          # re-run to update (detects existing)
# curl ... | bash                  # piped works too (no stdin issues)
#
# Supports: Linux, macOS, WSL2, Termux
# Update: auto-stashes local changes, pulls latest, reinstalls deps

set -euo pipefail

# ═══════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════

REPO="m4xx101/fissure"
BRANCH="main"
INSTALL_DIR="${HOME}/.hermes/skills/red-teaming/fissure"

# Colors (safe for non-interactive)
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'

# ═══════════════════════════════════════════════════════════════════════
# WSL Detection
# ═══════════════════════════════════════════════════════════════════════

IS_WSL=false
if [ -f /proc/version ] && grep -qi microsoft /proc/version 2>/dev/null; then
    IS_WSL=true
fi

IS_TERMUX=false
if [ -n "${TERMUX_VERSION:-}" ] || [[ "${PREFIX:-}" == *"com.termux"* ]]; then
    IS_TERMUX=true
fi

# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════

log()  { echo -e "${GREEN}✓${NC} $1"; }
info() { echo -e "${CYAN}→${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }

# ═══════════════════════════════════════════════════════════════════════
# Banner
# ═══════════════════════════════════════════════════════════════════════

echo ""
echo -e "${CYAN}${BOLD}  ⬡ FISSURE — Installer / Updater${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════
# Dependency checks
# ═══════════════════════════════════════════════════════════════════════

PYTHON="python3"
if $IS_WSL && command -v python3.exe &>/dev/null; then
    PYTHON="python3.exe"
elif $IS_TERMUX; then
    PYTHON="python"
fi

for cmd in git "$PYTHON" curl; do
    cmd_path=$(command -v "$cmd" 2>/dev/null || true)
    if [ -z "$cmd_path" ]; then
        err "Required: $cmd is not installed."
        case "$cmd" in
            git)    echo "  Install: sudo apt install git  |  brew install git  |  winget install Git.Git" ;;
            python*) echo "  Install: sudo apt install python3  |  brew install python  |  winget install Python.Python" ;;
            curl)   echo "  Install: sudo apt install curl  |  brew install curl" ;;
        esac
        exit 1
    fi
done

info "Python: $($PYTHON --version 2>/dev/null || echo 'unknown')"
info "Git:    $(git --version 2>/dev/null || echo 'unknown')"

# ═══════════════════════════════════════════════════════════════════════
# WSL-specific notes
# ═══════════════════════════════════════════════════════════════════════

if $IS_WSL; then
    warn "WSL detected — using $PYTHON"
    echo "  ⚠ If you see permission errors, the Windows filesystem (/mnt/c/)"
    echo "    may be interfering. Run this from your Linux home directory (~)."
    echo "  ⚠ If 'git pull' fails with file locking errors, try:"
    echo "    git config core.filemode false"
    echo "    git config core.autocrlf false"
    echo ""
fi

# ═══════════════════════════════════════════════════════════════════════
# Clone or Update
# ═══════════════════════════════════════════════════════════════════════

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Existing install found at $INSTALL_DIR"
    echo ""

    cd "$INSTALL_DIR"

    # Stash any local changes (safe — --include-untracked preserves new files)
    HAS_LOCAL=false
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        HAS_LOCAL=true
        STASH_NAME="fissure-update-$(date -u +%Y%m%d-%H%M%S)"
        info "Local changes detected — stashing before update..."
        git stash push --include-untracked -m "$STASH_NAME" 2>/dev/null || true
    fi

    # Fetch latest
    info "Fetching updates..."
    if ! git fetch origin 2>/dev/null; then
        err "Failed to fetch from origin. Check network."
        if $HAS_LOCAL; then
            warn "Local changes stashed. Restore with: git stash pop"
        fi
        exit 1
    fi

    # Check for updates
    NEW_COMMITS=$(git rev-list HEAD..origin/"$BRANCH" --count 2>/dev/null || echo "0")
    if [ "$NEW_COMMITS" -eq 0 ] 2>/dev/null; then
        log "Already up to date!"
        # Even if no code changes, ensure deps are fresh
        if [ -f "requirements.txt" ]; then
            info "Ensuring dependencies are installed..."
            $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || true
        fi
    else
        info "Found $NEW_COMMITS new commit(s)"
        info "Pulling latest code..."

        # Try fast-forward first, fall back to hard reset
        if ! git pull --ff-only origin "$BRANCH" 2>/dev/null; then
            warn "Fast-forward failed (history may have diverged) — resetting to match remote..."
            git reset --hard origin/"$BRANCH"
        fi

        log "Code updated!"

        # Reinstall dependencies
        if [ -f "pyproject.toml" ]; then
            info "Updating Python dependencies..."
            $PYTHON -m pip install -e . --quiet 2>/dev/null || true
        elif [ -f "requirements.txt" ]; then
            info "Updating Python dependencies..."
            $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || true
        fi
    fi

    # Clear stale .pyc cache
    find "$INSTALL_DIR" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

    # Restore stashed changes (only prompt if interactive)
    if $HAS_LOCAL; then
        if [ -t 0 ] && [ -t 1 ]; then
            echo ""
            warn "Local changes were stashed before updating."
            printf "Restore local changes now? [Y/n] "
            read -r restore_answer
            case "${restore_answer:-Y}" in
                y|Y|yes|YES|Yes|"")
                    git stash pop 2>/dev/null || true
                    log "Local changes restored."
                    ;;
                *)
                    info "Local changes left in stash. Restore with: git stash pop"
                    ;;
            esac
        else
            info "Local changes stashed (auto-restore skipped in non-interactive mode)"
            info "  Restore with: cd $INSTALL_DIR && git stash pop"
        fi
    fi
else
    info "Installing to $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"

    # Try SSH first (if user has keys configured), fall back to HTTPS
    info "Cloning repository..."
    if GIT_SSH_COMMAND="ssh -o BatchMode=yes -o ConnectTimeout=5" \
       git clone --branch "$BRANCH" "git@github.com:$REPO.git" "$INSTALL_DIR" 2>/dev/null; then
        log "Cloned via SSH"
    else
        rm -rf "$INSTALL_DIR" 2>/dev/null || true
        if git clone --depth 1 --branch "$BRANCH" "https://github.com/$REPO.git" "$INSTALL_DIR"; then
            log "Cloned via HTTPS"
        else
            err "Failed to clone repository."
            exit 1
        fi
    fi

    cd "$INSTALL_DIR"

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        info "Installing Python dependencies..."
        $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || true
    fi
fi

# ═══════════════════════════════════════════════════════════════════════
# Wiki Bootstrap
# ═══════════════════════════════════════════════════════════════════════

info "Bootstrapping session wiki..."
$PYTHON "$INSTALL_DIR/scripts/wiki.py" bootstrap 2>/dev/null || true

# ═══════════════════════════════════════════════════════════════════════
# Check optional deps
# ═══════════════════════════════════════════════════════════════════════

if command -v ollama &>/dev/null; then
    log "Ollama found — local model testing available"
else
    info "ollama not found (optional) — install for local model testing"
fi

if [ -d "${HOME}/.hermes/skills/red-teaming/godmode" ]; then
    log "G0DM0D3 skill found — parseltongue encoding available"
else
    info "G0DM0D3 skill not found (optional) — install for full Parseltongue support"
    echo "   hermes skill godmode"
fi

# ═══════════════════════════════════════════════════════════════════════
# Success / Update Info
# ═══════════════════════════════════════════════════════════════════════

echo ""
if [ "$NEW_COMMITS" -gt 0 ] 2>/dev/null; then
    log "⬡ FISSURE updated to latest!"
else
    log "⬡ FISSURE installed!"
fi
echo ""
echo "  To run a session:"
echo "    tell your agent: '🔥 Fissure — test [model/URL] for safety bypass'"
echo "    or: /fissure {url}"
echo ""
echo "  To update later:"
echo "    re-run this installer (handles updates)"
echo "    or: cd $INSTALL_DIR && git pull"
echo "    or tell the agent: /fissure_update"
echo ""
echo "  Docs: $INSTALL_DIR/README.md"
echo "  Wiki: ~/.hermes/wiki/fissure/"
echo ""
