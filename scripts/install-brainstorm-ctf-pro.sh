#!/usr/bin/env bash
# ⬡ FISSURE — Legacy installer redirect (old name)
# curl -fsSL .../install-brainstorm-ctf-pro.sh | bash → just calls install-fissure.sh
# Backward-compatible alias for the real installer.

set -euo pipefail
echo "ℹ️  Renamed to install-fissure.sh — redirecting..."
exec "$(dirname "$0")/install-fissure.sh" "$@"
