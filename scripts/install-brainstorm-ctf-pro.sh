#!/usr/bin/env bash
###############################################################################
# install-brainstorm-ctf-pro.sh
# Usage: curl -fsSL https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/refs/heads/main/scripts/install-brainstorm-ctf-pro.sh | bash
###############################################################################
set -euo pipefail
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
info()  { echo -e "${CYAN}  $1${NC}"; }
ok()    { echo -e "${GREEN}+ $1${NC}"; }
warn()  { echo -e "${YELLOW}! $1${NC}"; }
err()   { echo -e "${RED}x $1${NC}"; }
hdr()   { echo; echo -e "${BOLD}== $1 ==${NC}"; }

REPO="https://github.com/m4xx101/brainstorm-ctf-pro.git"
SKILL_DIR="${HOME}/.hermes/skills/red-teaming/brainstorm-ctf-pro"
WIKI="${WIKI_PATH:-${HOME}/ctf-wiki}"

hdr "Brainstorm-CTF-Pro Setup"
info "Skill: $SKILL_DIR"
info "Wiki:  $WIKI"

# Prerequisites
hdr "Checking prerequisites"
command -v git &>/dev/null && ok "$(git --version)" || { err "git required"; exit 1; }
command -v python3 &>/dev/null && ok "$(python3 --version)" || { err "python3 required"; exit 1; }
pip install pymupdf pymupdf4llm 2>&1 | tail -1 && ok "pymupdf installed" || warn "pymupdf failed -- PDF payloads disabled"

# Clone or update
hdr "Installing skill"
if [ -d "$SKILL_DIR/.git" ]; then
  cd "$SKILL_DIR" && git pull origin main 2>/dev/null && ok "Updated" || warn "Update failed, using current"
elif [ -d "$SKILL_DIR" ]; then
  warn "Directory exists but not a git repo"
else
  mkdir -p "$(dirname "$SKILL_DIR")" && git clone "$REPO" "$SKILL_DIR" 2>&1 | tail -1 && ok "Cloned" || { err "Clone failed"; exit 1; }
fi

# Wiki
hdr "Setting up knowledge base"
mkdir -p "$WIKI"/{raw/{targets,payloads,responses},targets,techniques,comparisons,queries}
[ -f "$WIKI/SCHEMA.md" ] || cp "$SKILL_DIR/templates/wiki-schema.md" "$WIKI/SCHEMA.md" 2>/dev/null || true
[ -f "$WIKI/index.md" ] || printf "# CTF Wiki Index\n\n## Targets\n## Techniques\n## Comparisons\n## Queries\n" > "$WIKI/index.md"
[ -f "$WIKI/log.md" ] || printf "# CTF Wiki Log\n\n## [$(date +%Y-%m-%d)] create | Wiki initialized\n" > "$WIKI/log.md"
ok "Wiki structure ready"

# Ollama check
hdr "Checking local models"
if curl -s http://localhost:11434/api/tags | python3 -c "import sys,json;models=json.load(sys.stdin).get('models',[]);\nfor m in models: print(f'  - {m[\"name\"]} ({m.get(\"details\",{}).get(\"family\",\"?\")}  ')')" 2>/dev/null; then
  ok "Ollama running with local models"
else
  warn "Ollama not running (--ollama mode will be unavailable)"
  warn "Install: https://ollama.ai -- then run: ollama serve"
fi

# Verify
hdr "Verification"
[ -f "$SKILL_DIR/SKILL.md" ] && ok "Skill installed" || err "Skill missing"
[ -f "$WIKI/SCHEMA.md" ] && ok "Wiki configured" || err "Wiki missing"
python3 -c "import pymupdf" 2>/dev/null && ok "PDF payloads ready" || warn "PDF payloads disabled"
echo; echo "Restart Hermes to load the new skill."
