<#
.SYNOPSIS
    Sprint 23 Q7: Audit the 'sessions' table size and recommend dropping
    it if unused since ADR-0024 Bearer migration.

.DESCRIPTION
    Runs a SQL query against the production DB to get the sessions table
    size. If > 0 and the table is confirmed unused, generates an Alembic
    migration to drop it.

.USAGE
    pwsh scripts/audit-sessions-table.ps1

.NOTES
    Requires DATABASE_URL in environment or .env file.
#>
$ErrorActionPreference = "Stop"

Write-Host "=== Sprint 23 Q7 — Sessions Table Audit ===" -ForegroundColor Cyan

# Load DATABASE_URL from env or .env
$dbUrl = $env:DATABASE_URL
if (-not $dbUrl) {
    $envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
    if (Test-Path $envFile) {
        $line = Get-Content $envFile | Where-Object { $_ -match '^DATABASE_URL=' }
        if ($line) { $dbUrl = ($line -split '=', 2)[1].Trim() }
    }
}

if (-not $dbUrl) {
    throw "DATABASE_URL not found in environment or .env file."
}

# Use psql if available, else warn
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    Write-Host "psql not found. Install PostgreSQL client or use a different method." -ForegroundColor Red
    exit 1
}

# Extract connection info from URL (postgresql://user:pass@host:port/db)
$parsed = [System.Uri]$dbUrl
$dbHost = $parsed.Host
$dbPort = if ($parsed.Port -gt 0) { $parsed.Port } else { 5432 }
$dbName = $parsed.AbsolutePath.TrimStart('/')
$userInfo = $parsed.UserInfo -split ':'
$dbUser = $userInfo[0]
$dbPass = $userInfo[1]

$env:PGPASSWORD = $dbPass

$sizeSql = "SELECT pg_size_pretty(pg_total_relation_size('sessions')) AS size;"
$sizeResult = & psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c $sizeSql -t -A 2>&1

Write-Host "`nsessions table size: $sizeResult" -ForegroundColor Yellow

$countSql = "SELECT COUNT(*) FROM sessions;"
$countResult = & psql -h $dbHost -p $dbPort -U $dbUser -d $dbName -c $countSql -t -A 2>&1
Write-Host "sessions row count: $countResult" -ForegroundColor Yellow

if ($countResult.Trim() -eq "0" -or $sizeResult.Trim() -eq "0 bytes") {
    Write-Host "`nTable is empty or tiny. Safe to drop." -ForegroundColor Green
    Write-Host "Generating Alembic migration to drop sessions table..." -ForegroundColor Cyan

    $repoRoot = Split-Path -Parent $PSScriptRoot
    Push-Location $repoRoot
    try {
        python -m alembic revision -m "drop unused sessions table"
        Write-Host "Migration created. Review and apply with:" -ForegroundColor Green
        Write-Host "  python -m alembic upgrade head" -ForegroundColor DarkGray
    } finally {
        Pop-Location
    }
} else {
    Write-Host "`nTable has data. Do NOT drop without confirming rows are stale." -ForegroundColor Red
    Write-Host "Inspect rows: SELECT * FROM sessions LIMIT 5;" -ForegroundColor DarkGray
}
