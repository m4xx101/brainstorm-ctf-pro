###############################################################################
# install-brainstorm-ctf-pro.ps1  (Windows)
# Usage: irm https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/refs/heads/main/scripts/install-brainstorm-ctf-pro.ps1 | iex
###############################################################################
$ErrorActionPreference = "Stop"
$G = @{ForegroundColor="Green"}; $C = @{ForegroundColor="Cyan"}; $Y = @{ForegroundColor="Yellow"}; $R = @{ForegroundColor="Red"}
function ok  { Write-Host ("+ " + $args[0]) @G }
function inf { Write-Host ("  " + $args[0]) @C }
function wrn { Write-Host ("! " + $args[0]) @Y }
function err { Write-Host ("x " + $args[0]) @R }

$Repo  = "https://github.com/m4xx101/brainstorm-ctf-pro.git"
$Skill = "$env:USERPROFILE\.hermes\skills\red-teaming\brainstorm-ctf-pro"
$Wiki  = "$env:USERPROFILE\ctf-wiki"

Write-Host "`n=== Brainstorm-CTF-Pro (Windows) ==="
inf "Skill: $Skill"
inf "Wiki:  $Wiki"

# Prereqs
if (!(Get-Command git -ea 0))   { err "git required"; return } else { ok (git --version) }
if (!(Get-Command python -ea 0)) { err "python3 required"; return } else { ok (python --version) }

# Install pymupdf
try  { pip install pymupdf pymupdf4llm 2>$null; ok "pymupdf installed" }
catch{ wrn "pymupdf failed -- try: pip install --only-binary :all: pymupdf" }

# Clone
if (!(Test-Path $Skill)) {
    New-Item -ItemType Directory -Force (Split-Path $Skill -Parent) > $null
    git clone $Repo $Skill 2>$null | Out-Null
    ok "Cloned"
} else { ok "Already installed" }

# Wiki
New-Item -Force -ItemType Directory "$Wiki\raw\targets",$Wiki\raw\payloads,$Wiki\raw\responses,$Wiki\targets,$Wiki\techniques,$Wiki\comparisons,$Wiki\queries > $null
ok "Wiki structure ready"

# Ollama check
try {
    $r = curl -s http://localhost:11434/api/tags 2>$null
    if ($r) { ok "Ollama running" } else { wrn "Ollama not running" }
} catch { wrn "Ollama not running -- install from https://ollama.ai" }

# Link
[Environment]::SetEnvironmentVariable("WIKI_PATH", $Wiki, "User")
ok "WIKI_PATH set permanently"

Write-Host "`nRestart Hermes to load the skill." @C
