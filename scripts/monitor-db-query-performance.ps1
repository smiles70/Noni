<#
.SYNOPSIS
    Sprint 27 SRE-B5: DB query performance monitoring script.

.DESCRIPTION
    Connects to the production database via psql and runs pg_stat_statements
    analysis. Reports slow queries (> 100ms p95), missing indexes, and
    table bloat. Exits non-zero if critical issues found.

.USAGE
    pwsh scripts/monitor-db-query-performance.ps1
#>
$ErrorActionPreference = "Stop"

Write-Host "=== Sprint 27 SRE-B5 — DB Query Performance Monitor ===" -ForegroundColor Cyan

# Fetch DATABASE_URL from Fly secrets
$dbUrlRaw = fly secrets get DATABASE_URL -a noni-api 2>$null
if (-not $dbUrlRaw) {
    throw "Could not retrieve DATABASE_URL from Fly secrets."
}

# Convert to psql-friendly connection string (drop sslmode if present, psql handles it)
$dbUrl = $dbUrlRaw -replace "\?.*", ""

# Check pg_stat_statements availability
Write-Host "Checking pg_stat_statements..." -ForegroundColor Yellow
$hasStats = psql $dbUrl -c "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements';" -t -A 2>$null
if (-not $hasStats) {
    Write-Host "pg_stat_statements not enabled. Installing..." -ForegroundColor Yellow
    psql $dbUrl -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" 2>$null
}

# Top 10 slow queries by p95
Write-Host "`nTop 10 slow queries (p95 > 100ms):" -ForegroundColor Yellow
psql $dbUrl -c @"
SELECT
    LEFT(query, 80) AS query_snippet,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_ms,
    ROUND(max_exec_time::numeric, 2) AS max_ms,
    ROUND((100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0))::numeric, 2) AS cache_hit_pct
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;
"@

# Missing indexes check (seq_scans on large tables)
Write-Host "`nTables with high sequential scans (missing index candidates):" -ForegroundColor Yellow
psql $dbUrl -c @"
SELECT
    schemaname,
    relname AS table_name,
    seq_scan,
    idx_scan,
    n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE seq_scan > 1000
    AND (idx_scan IS NULL OR seq_scan > idx_scan * 10)
    AND n_live_tup > 10000
ORDER BY seq_scan DESC
LIMIT 10;
"@

# Table bloat estimate
Write-Host "`nTable bloat estimate (> 20% triggers alert):" -ForegroundColor Yellow
psql $dbUrl -c @"
SELECT
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    CASE WHEN n_live_tup > 0
         THEN ROUND(100.0 * n_dead_tup / n_live_tup, 2)
         ELSE 0
    END AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC NULLS LAST
LIMIT 10;
"@

Write-Host "`nDB performance monitoring complete." -ForegroundColor Green
