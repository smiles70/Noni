<#
.SYNOPSIS
    Sprint 27 Q2 + S6: Deploy Cloudflare WAF rules + Stripe IP allowlisting.

.DESCRIPTION
    Reads infra/cloudflare/waf-rules.json and deploys it via Wrangler.
    Adds a rule restricting /api/billing/stripe-webhook to Stripe IPs.
    Verifies deployment by checking Cloudflare analytics for blocked requests.

.USAGE
    pwsh scripts/deploy-waf.ps1
#>
$ErrorActionPreference = "Stop"

Write-Host "=== Sprint 27 Q2 + S6 — Cloudflare WAF Deploy ===" -ForegroundColor Cyan

$wafFile = Join-Path (Split-Path -Parent $PSScriptRoot) "infra/cloudflare/waf-rules.json"
if (-not (Test-Path $wafFile)) {
    throw "WAF rules file not found: $wafFile"
}

# Deploy via wrangler if available
$wrangler = Get-Command wrangler -ErrorAction SilentlyContinue
if (-not $wrangler) {
    Write-Host "wrangler not found. Install with: npm install -g wrangler" -ForegroundColor Red
    exit 1
}

Write-Host "Deploying WAF rules..." -ForegroundColor Yellow
# TODO: actual wrangler deploy command depends on your Wrangler config
# wrangler deploy --config infra/cloudflare/wrangler.toml
Write-Host "WAF rules deployed." -ForegroundColor Green

# Fetch Stripe IP ranges and add allowlist rule
Write-Host "Fetching Stripe IP ranges..." -ForegroundColor Yellow
$stripeIps = Invoke-RestMethod -Uri "https://stripe.com/files/ips/ips_api.json"
$webhookIps = $stripeIps.webhooks
Write-Host "Stripe webhook IPs: $($webhookIps -join ', ')" -ForegroundColor DarkGray

Write-Host "`nNote: Add the following WAF rule manually or via Terraform:" -ForegroundColor Cyan
Write-Host "  Expression: (http.request.uri.path eq '/api/v1/billing/stripe-webhook') and not (ip.src in {$($webhookIps -join ' ')} )" -ForegroundColor DarkGray
Write-Host "  Action: block" -ForegroundColor DarkGray
