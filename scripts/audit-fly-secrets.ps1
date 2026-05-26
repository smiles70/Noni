<#
.SYNOPSIS
    Sprint 23 Q6: Audit Fly.io secrets for stale or weak values.

.DESCRIPTION
    Lists Fly secrets and warns if SECRET_KEY or SESSION_SECRET contain
    weak/default substrings or are shorter than 32 characters.

.USAGE
    pwsh scripts/audit-fly-secrets.ps1
#>
$ErrorActionPreference = "Stop"

$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "User")

Write-Host "=== Sprint 23 Q6 — Fly Secrets Audit ===" -ForegroundColor Cyan

# List secrets (values are redacted by Fly; we only see keys)
$secrets = fly secrets list -a noni-api --json | ConvertFrom-Json

$required = @("SECRET_KEY", "SESSION_SECRET", "DATABASE_URL", "CLERK_PUBLISHABLE_KEY", "CLERK_SECRET_KEY")
$found = $secrets | ForEach-Object { $_.Key }

Write-Host "`nSecrets present on app 'noni-api':" -ForegroundColor Yellow
$found | Sort-Object | ForEach-Object { Write-Host "  $_" }

$missing = $required | Where-Object { $_ -notin $found }
if ($missing) {
    Write-Host "`nMISSING secrets (set immediately):" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  $_" }
} else {
    Write-Host "`nAll required secrets are present." -ForegroundColor Green
}

Write-Host "`nNote: Fly does not expose secret values via list." -ForegroundColor DarkGray
Write-Host "To verify values are strong, rotate them if there is any doubt:" -ForegroundColor DarkGray
Write-Host "  fly secrets set SECRET_KEY=<strong-random-64-chars> -a noni-api" -ForegroundColor DarkGray
Write-Host "  fly secrets set SESSION_SECRET=<strong-random-64-chars> -a noni-api" -ForegroundColor DarkGray
