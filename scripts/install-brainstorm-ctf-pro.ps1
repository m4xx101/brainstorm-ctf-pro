# ⬡ FISSURE — PowerShell installer (legacy name redirect)
# iwr -Uri https://raw.githubusercontent.com/m4xx101/fissure/main/scripts/install-brainstorm-ctf-pro.ps1 -UseBasicParsing | iex
Write-Host "ℹ️ Renamed to install-fissure.ps1 — redirecting..." -ForegroundColor Yellow
$scriptPath = "$PSScriptRoot\install-fissure.ps1"
if (-not (Test-Path $scriptPath)) {
    $scriptPath = "$env:USERPROFILE\.hermes\skills\red-teaming\fissure\scripts\install-fissure.ps1"
}
& $scriptPath @args
exit $LASTEXITCODE
