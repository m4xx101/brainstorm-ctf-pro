# brainstorm-ctf-pro — PowerShell installer
# iwr -Uri https://raw.githubusercontent.com/m4xx101/brainstorm-ctf-pro/main/scripts/install-brainstorm-ctf-pro.ps1 -UseBasicParsing | iex

$ErrorActionPreference = "Stop"
$Repo = "m4xx101/brainstorm-ctf-pro"
$Branch = "main"
$InstallDir = "$env:USERPROFILE\.hermes\skills\red-teaming\brainstorm-ctf-pro"

Write-Host "🧠 Installing brainstorm-ctf-pro..." -ForegroundColor Cyan

# Check Python
try {
    $pyVersion = python --version 2>&1
    Write-Host "✅ Python: $pyVersion"
} catch {
    Write-Host "❌ Python not found. Install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Check git
try {
    $null = git --version
    Write-Host "✅ Git found"
} catch {
    Write-Host "❌ Git not found. Install from git-scm.com" -ForegroundColor Red
    exit 1
}

# Clone or update
if (Test-Path "$InstallDir\.git") {
    Write-Host "📦 Updating existing install at $InstallDir..." -ForegroundColor Yellow
    Push-Location $InstallDir
    git pull origin $Branch --ff-only
    Pop-Location
} else {
    Write-Host "📦 Cloning to $InstallDir..." -ForegroundColor Yellow
    $parent = Split-Path $InstallDir -Parent
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    git clone --depth 1 "https://github.com/$Repo.git" $InstallDir
}

# Bootstrap wiki
Write-Host "📝 Bootstrapping session wiki..." -ForegroundColor Yellow
try {
    python "$InstallDir/scripts/wiki.py" bootstrap
} catch {
    Write-Host "ℹ️  Wiki bootstrap note: $_" -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "✅ brainstorm-ctf-pro installed!" -ForegroundColor Green
Write-Host ""
Write-Host "To start: tell your agent 'Run brainstorm-ctf-pro against [target]'" -ForegroundColor Cyan
Write-Host "Docs: $InstallDir\README.md" -ForegroundColor Cyan
Write-Host ""
