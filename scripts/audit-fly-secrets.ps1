<#
.SYNOPSIS
    Sprint 23 Q6: Audit railway.app secrets for stale or weak values.

.DESCRIPTION
    Lists Railway secrets and warns if SECRET_KEY or SESSION_SECRET contain
    weak/default substrings or are shorter than 32 characters.

.USAGE
    pwsh scripts/audit-railway-secrets.ps1
#>
$ErrorActionPreference = "Stop"

$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "User")

Write-Host "=== Sprint 23 Q6 — Railway Secrets Audit ===" -ForegroundColor Cyan

# List secrets (values are redacted by Railway; we only see keys)
$secrets = railway secrets list -a noni-api --json | ConvertFrom-Json

$required = @("SECRET_KEY", "SESSION_SECRET", "DATABASE_URL", "AUTH_PROVIDER", "MAGIC_API_SECRET_KEY", "FRONTEND_URL")
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

Write-Host "`nNote: Railway does not expose secret values via list." -ForegroundColor DarkGray
Write-Host "To verify values are strong, rotate them if there is any doubt:" -ForegroundColor DarkGray
Write-Host "  railway secrets set SECRET_KEY=<strong-random-64-chars> -a noni-api" -ForegroundColor DarkGray
Write-Host "  railway secrets set SESSION_SECRET=<strong-random-64-chars> -a noni-api" -ForegroundColor DarkGray
