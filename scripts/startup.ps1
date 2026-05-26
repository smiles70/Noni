<#
.SYNOPSIS
    Noni local startup script. Boots backend (FastAPI/uvicorn) and frontend (Vite dev server) in parallel.

.USAGE
    From repo root:
        pwsh scripts/startup.ps1
    or:
        .\scripts\startup.ps1

.PARAMETERS
    -BackendPort     Port for FastAPI (default 8000)
    -FrontendPort    Port for Vite (default 5173)
    -SkipInstall     Skip dependency install steps
    -Prod            Point frontend at prod backend (https://noni-api.fly.dev) instead of localhost

.NOTES
    Opens two new PowerShell windows so each service streams its own logs.
    Close those windows (or Ctrl+C inside each) to stop the services.
#>
[CmdletBinding()]
param(
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173,
    [switch]$SkipInstall,
    [switch]$Prod
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== Noni Startup ===" -ForegroundColor Cyan
Write-Host "Repo:     $RepoRoot"
Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host ""

# Ensure PATH includes Node and Fly installs (Windows persistent env vars)
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "User")

# ---------- Backend ----------
$backendDir = Join-Path $RepoRoot "backend"
if (-not (Test-Path $backendDir)) { throw "Backend directory not found: $backendDir" }

# Pick a python interpreter
$python = $null
foreach ($candidate in @("python", "py", "python3")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) { $python = $candidate; break }
}
if (-not $python) { throw "No Python interpreter found on PATH." }

if (-not $SkipInstall) {
    Write-Host "[backend] Installing Python dependencies..." -ForegroundColor Yellow
    $reqFile = Join-Path $RepoRoot "requirements.txt"
    if (Test-Path $reqFile) {
        & $python -m pip install --quiet --disable-pip-version-check -r $reqFile
    } else {
        Write-Host "  (no requirements.txt found, skipping)" -ForegroundColor DarkGray
    }
}

# ---------- Frontend ----------
$frontendDir = Join-Path $RepoRoot "frontend"
if (-not (Test-Path $frontendDir)) { throw "Frontend directory not found: $frontendDir" }

if (-not $SkipInstall) {
    Write-Host "[frontend] Installing npm dependencies..." -ForegroundColor Yellow
    Push-Location $frontendDir
    try { npm install --silent } finally { Pop-Location }
}

# ---------- Launch ----------
$apiBaseUrl = if ($Prod) { "https://noni-api.fly.dev" } else { "http://localhost:$BackendPort" }

Write-Host ""
Write-Host "[backend] Launching uvicorn..." -ForegroundColor Green
$backendCmd = "Set-Location '$RepoRoot'; `$env:PYTHONPATH = '$RepoRoot'; & $python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port $BackendPort"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

Start-Sleep -Seconds 2

Write-Host "[frontend] Launching vite dev server..." -ForegroundColor Green
$frontendCmd = "Set-Location '$frontendDir'; `$env:VITE_API_BASE_URL = '$apiBaseUrl'; npm run dev -- --port $FrontendPort"
Start-Process pwsh -ArgumentList "-NoExit", "-Command", $frontendCmd -WindowStyle Normal

Write-Host ""
Write-Host "=== Startup complete ===" -ForegroundColor Cyan
Write-Host "Backend  -> http://localhost:$BackendPort/docs"
Write-Host "Frontend -> http://localhost:$FrontendPort"
Write-Host "API base -> $apiBaseUrl"
Write-Host ""
Write-Host "Close the two spawned PowerShell windows to stop the services." -ForegroundColor DarkGray
