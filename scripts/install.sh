#!/usr/bin/env bash
# brainstorm-ctf-pro — install script
# Usage: curl -fsSL https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/main/scripts/install.sh | bash

set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/brainstorm-ctf-pro}"
GODMODE_SKILL_DIR="$HOME/.hermes/skills/red-teaming/godmode"

echo "==> brainstorm-ctf-pro installer"
echo "    Target: $INSTALL_DIR"

# --- Dependencies ---
if ! command -v git &>/dev/null; then
    echo "ERROR: git is required. Install with: apt install git -y"
    exit 1
fi

# --- Clone repo ---
if [ -d "$INSTALL_DIR" ]; then
    echo "==> Directory exists — pulling latest..."
    cd "$INSTALL_DIR" && git pull --ff-only
else
    echo "==> Cloning repository..."
    git clone https://github.com/m4xx101/brainstorm-ctf-pro.git "$INSTALL_DIR"
fi

# --- Check godmode skill ---
if [ ! -d "$GODMODE_SKILL_DIR/scripts" ]; then
    echo "==> WARNING: GODMODE skill not found at $GODMODE_SKILL_DIR"
    echo "    The godmode skill is REQUIRED for payload generation."
    echo "    Install the godmode skill before using brainstorm-ctf-pro."
    echo ""
    echo "    Expected structure:"
    echo "      $GODMODE_SKILL_DIR/scripts/parseltongue.py"
    echo "      $GODMODE_SKILL_DIR/scripts/load_godmode.py"
    echo "      $GODMODE_SKILL_DIR/scripts/godmode_race.py"
    echo "      $GODMODE_SKILL_DIR/scripts/auto_jailbreak.py"
fi

# --- Python deps ---
if command -v pip3 &>/dev/null; then
    echo "==> Installing Python dependencies..."
    pip3 install openai pyyaml 2>/dev/null || true
fi

echo ""
echo "==> ✅ INSTALLED at $INSTALL_DIR"
echo ""
echo "    Quick start:"
echo "      cd $INSTALL_DIR"
echo "      python3 -c \"from generators.payload_factory import PayloadFactory; print('OK')\""
echo ""
echo "    Run with:"
echo "      python3 -c \"from engine.orchestrator import run_session; r=run_session('test'); print(r['verdict'])\""
