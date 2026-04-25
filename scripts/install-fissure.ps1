# ⬡ FISSURE — PowerShell installer (Windows / WSL)
# iwr -Uri https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.ps1 -UseBasicParsing | iex
#
# Supports: Windows native (PowerShell 5+), WSL (via wsl.exe)
# Update: If already installed, pulls latest + reinstalls deps

$ErrorActionPreference = "Stop"
$Repo = "m4xx101/fissure"
$Branch = "main"
$InstallDir = "$env:USERPROFILE\.hermes\skills\red-teaming\fissure"
$WslInstallDir = "/home/$env:USERNAME/.hermes/skills/red-teaming/fissure"

Write-Host ""
Write-Host "  ⬡ FISSURE — Installer / Updater" -ForegroundColor Cyan
Write-Host ""

# ── WSL detection ──
$IsWsl = $false
if (Get-Command wsl.exe -ErrorAction SilentlyContinue) {
    try {
        $uname = wsl.exe uname -a 2>$null
        if ($uname -match "microsoft|WSL|wsl") {
            $IsWsl = $true
        }
    } catch {}
}

# ── WSL mode ──
if ($IsWsl) {
    Write-Host "WSL detected — installing via wsl.exe" -ForegroundColor Yellow
    Write-Host ""

    # Check if wsl has the required tools
    $commands = @("git", "python3", "curl")
    foreach ($cmd in $commands) {
        $found = wsl.exe bash -c "command -v $cmd 2>/dev/null && echo YES || echo NO"
        if ($found -ne "YES") {
            Write-Host "❌ $cmd not found inside WSL." -ForegroundColor Red
            Write-Host "   Install it: wsl.exe sudo apt install $cmd" -ForegroundColor Yellow
            exit 1
        }
    }

    # Delegate to the bash installer inside WSL
    Write-Host "Running install-fissure.sh inside WSL..." -ForegroundColor Cyan
    $installUrl = "https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-fissure.sh"
    wsl.exe bash -c "curl -fsSL $installUrl | bash"
    exit $LASTEXITCODE
}

# ── Native Windows ──
$git = Get-Command git -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Host "❌ Git not found. Install from git-scm.com" -ForegroundColor Red
    exit 1
}
if (-not $python) {
    Write-Host "❌ Python not found. Install from python.org" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Python: $(& $python.Source --version 2>&1)" -ForegroundColor Green
Write-Host "✓ Git:    $(& $git.Source --version 2>&1)" -ForegroundColor Green
Write-Host ""

# ── Update existing ──
if (Test-Path "$InstallDir\.git") {
    Write-Host "Existing install found at $InstallDir" -ForegroundColor Cyan
    Push-Location $InstallDir

    # Stash local changes
    $hasLocal = $false
    try {
        $status = & git status --porcelain
        if ($status) {
            $hasLocal = $true
            Write-Host "→ Stashing local changes..." -ForegroundColor Yellow
            & git stash push --include-untracked -m "fissure-update-$(Get-Date -Format 'yyyyMMdd-HHmmss')" 2>$null
        }
    } catch {}

    # Fetch + pull
    Write-Host "→ Fetching updates..." -ForegroundColor Cyan
    & git fetch origin 2>$null
    $newCommits = & git rev-list HEAD..origin/$Branch --count 2>$null

    if ([int]$newCommits -gt 0) {
        Write-Host "→ Found $newCommits new commit(s)" -ForegroundColor Cyan
        Write-Host "→ Pulling latest code..." -ForegroundColor Cyan
        try {
            & git pull --ff-only origin $Branch 2>$null
        } catch {
            Write-Host "⚠ Fast-forward failed — resetting..." -ForegroundColor Yellow
            & git reset --hard origin/$Branch 2>$null
        }
        Write-Host "✓ Code updated!" -ForegroundColor Green

        # Reinstall deps
        if (Test-Path "requirements.txt") {
            Write-Host "→ Updating dependencies..." -ForegroundColor Cyan
            & python -m pip install -r requirements.txt --quiet 2>$null
        }
    } else {
        Write-Host "✓ Already up to date!" -ForegroundColor Green
    }

    # Restore stash
    if ($hasLocal) {
        Write-Host ""
        Write-Host "⚠ Local changes were stashed during update." -ForegroundColor Yellow
        Write-Host "  Restore with: cd $InstallDir && git stash pop" -ForegroundColor Cyan
    }

    Pop-Location
}
# ── Fresh install ──
else {
    Write-Host "→ Installing to $InstallDir..." -ForegroundColor Cyan
    $parent = Split-Path $InstallDir -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null

    Write-Host "→ Cloning repository..." -ForegroundColor Cyan
    & git clone --depth 1 "https://github.com/$Repo.git" $InstallDir

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to clone repository" -ForegroundColor Red
        exit 1
    }

    Push-Location $InstallDir
    if (Test-Path "requirements.txt") {
        Write-Host "→ Installing dependencies..." -ForegroundColor Cyan
        & python -m pip install -r requirements.txt --quiet 2>$null
    }
    Pop-Location
}

# ── Wiki bootstrap ──
Push-Location $InstallDir
Write-Host "→ Bootstrapping wiki..." -ForegroundColor Cyan
try {
    & python scripts/wiki.py bootstrap 2>$null
} catch {}
Pop-Location

# ── Check optional deps ──
$hasOllama = Get-Command ollama -ErrorAction SilentlyContinue
if ($hasOllama) {
    Write-Host "✓ Ollama found — local model testing available" -ForegroundColor Green
} else {
    Write-Host "ℹ️  ollama not found (optional)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✓ ⬡ FISSURE installed!" -ForegroundColor Green
Write-Host ""
Write-Host "  To run: tell your agent '🔥 Fissure — test [model/URL]'"
Write-Host "  Docs:   $InstallDir\README.md"
Write-Host "  Update: cd $InstallDir && git pull"
Write-Host ""
