#!/usr/bin/env bash
set -euo pipefail

# ── brainstorm-ctf-pro installer ─────────────────────────────────────────────
REPO="m4xx101/brainstorm-ctf-pro"
BRANCH="main"
INSTALL_DIR="${HOME}/.hermes/skills/red-teaming/brainstorm-ctf-pro"

echo "🧠 Installing brainstorm-ctf-pro..."

# Ensure dependencies
for cmd in git python3 curl; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "❌ Required: $cmd. Install it first."
        exit 1
    fi
done

# Clone or update
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "📦 Updating existing install in $INSTALL_DIR..."
    cd "$INSTALL_DIR"
    git pull origin "$BRANCH" --ff-only
else
    echo "📦 Cloning to $INSTALL_DIR..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone --depth 1 "https://github.com/$REPO.git" "$INSTALL_DIR"
fi

# Install Python deps if requirements exist
if [ -f "$INSTALL_DIR/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r "$INSTALL_DIR/requirements.txt" --quiet 2>/dev/null || true
fi

# Bootstrap wiki
echo "📝 Bootstrapping session wiki..."
python3 "$INSTALL_DIR/scripts/wiki.py" --action bootstrap 2>/dev/null || true

# Check for godmode skill (optional)
if [ -d "${HOME}/.hermes/skills/red-teaming/godmode" ]; then
    echo "✅ G0DM0D3 skill found — parseltongue encoding available"
else
    echo "ℹ️  G0DM0D3 skill not found (optional) — install for full Parseltongue support"
    echo "   hermes skill godmode"
fi

# Success
echo ""
echo "✅ brainstorm-ctf-pro installed!"
echo ""
echo "To start a session:"
echo "  hermes skill brainstorm-ctf-pro"
echo "  → Tell the agent: 'Test [model/URL] for safety bypass'"
echo ""
echo "To update:"
echo "  cd $INSTALL_DIR && git pull"
echo ""
