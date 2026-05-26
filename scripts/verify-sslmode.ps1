<#
.SYNOPSIS
    Sprint 27 Q1: Verify/enforce sslmode=require in production DATABASE_URL.

.DESCRIPTION
    Inspects the DATABASE_URL Fly secret. If sslmode=require is absent,
    updates the string and redeploys. Exits 0 if already present.

.USAGE
    pwsh scripts/verify-sslmode.ps1
#>
$ErrorActionPreference = "Stop"

Write-Host "=== Sprint 27 Q1 — Verify sslmode=require ===" -ForegroundColor Cyan

$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "User")

# Get DATABASE_URL from Fly secrets
$dbUrlRaw = fly secrets get DATABASE_URL -a noni-api 2>$null
if (-not $dbUrlRaw) {
    throw "Could not retrieve DATABASE_URL from Fly secrets."
}

if ($dbUrlRaw -match "sslmode=require") {
    Write-Host "PASS: DATABASE_URL contains sslmode=require" -ForegroundColor Green
    exit 0
}

Write-Host "MISSING: sslmode=require not found in DATABASE_URL" -ForegroundColor Red

# Append sslmode=require
$separator = if ($dbUrlRaw -match "\?") { "&" } else { "?" }
$newDbUrl = "$dbUrlRaw${separator}sslmode=require"

Write-Host "Updating Fly secret..." -ForegroundColor Yellow
fly secrets set "DATABASE_URL=$newDbUrl" -a noni-api
Write-Host "Redeploying to pick up new secret..." -ForegroundColor Yellow
fly deploy --remote-only -a noni-api
Write-Host "DONE: sslmode=require enforced." -ForegroundColor Green
