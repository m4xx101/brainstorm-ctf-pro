#!/usr/bin/env bash
# brainstorm-ctf-pro — one-shot installer
# curl -fsSL https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/main/scripts/install-brainstorm-ctf-pro.sh | bash

set -euo pipefail

REPO="m4xx101/brainstorm-ctf-pro"
BRANCH="main"
INSTALL_DIR="${HOME}/.hermes/skills/red-teaming/brainstorm-ctf-pro"

echo "🧠 Installing brainstorm-ctf-pro..."

# Check deps
for cmd in git python3 curl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "❌ Missing: $cmd. Install it first."
        exit 1
    fi
done

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "📦 Updating existing install at $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull origin "$BRANCH" --ff-only
else
    echo "📦 Cloning to $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 "https://github.com/$REPO.git" "$INSTALL_DIR"
fi

# Bootstrap wiki
echo "📝 Bootstrapping session wiki..."
python3 "$INSTALL_DIR/scripts/wiki.py" bootstrap 2>/dev/null || true

# Check optional deps
if command -v ollama &>/dev/null; then
    echo "✅ Ollama found — local model testing available"
else
    echo "ℹ️  ollama not found (optional) — install for local model testing"
fi

if [ -d "${HOME}/.hermes/skills/red-teaming/godmode" ]; then
    echo "✅ G0DM0D3 skill found — parseltongue encoding available"
else
    echo "ℹ️  G0DM0D3 skill not found (optional) — install via: hermes skill godmode"
fi

echo ""
echo "✅ brainstorm-ctf-pro installed!"
echo ""
echo "To start: tell your agent 'Run brainstorm-ctf-pro against [target]'"
echo "Docs: $INSTALL_DIR/README.md"
echo ""
