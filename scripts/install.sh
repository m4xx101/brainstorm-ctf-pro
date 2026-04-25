#!/usr/bin/env bash
# ⬡ FISSURE — Legacy installer redirect
# This file exists for backward compatibility.
# Use install-fissure.sh for the real installer.

set -euo pipefail
exec "$(dirname "$0")/install-fissure.sh" "$@"
