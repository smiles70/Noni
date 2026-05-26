#Requires -Version 5.1
<#
.SYNOPSIS
    Fix the production VITE_API_BASE_URL GitHub secret and trigger re-deploy.

.DESCRIPTION
    Automates checking and correcting the GitHub secret that controls
    where the frontend build points its API calls. Also triggers a
    workflow_dispatch re-deploy if the secret was wrong or stale.

    One-time setup: if gh CLI is not authenticated, run `gh auth login`
    before executing this script.
#>
[CmdletBinding()]
param(
    [string]$Repo = "smiles70/Noni",
    [string]$TargetUrl = "https://noni-api.fly.dev",
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Test-GhCli {
    try {
        $null = Get-Command gh -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Install-GhCli {
    Write-Host "GitHub CLI (gh) not found. Installing via winget..."
    try {
        $null = Get-Command winget -ErrorAction Stop
        winget install --id GitHub.cli --source winget --accept-package-agreements --accept-source-agreements
        # Refresh PATH so gh is available in this session
        $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
        Write-Host "gh installed. You may need to restart your terminal for it to be available."
    } catch {
        Write-Error "winget not available. Please install gh manually from https://cli.github.com/"
        exit 1
    }
}

function Test-GhAuth {
    $status = gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    return $true
}

function Get-GhSecretValue {
    param([string]$Name)
    # gh secret list doesn't show values (by design). We can only SET, not GET.
    # So we check the deployed artifact instead — or just always SET to be safe.
    return $null
}

function Set-GhSecret {
    param([string]$Name, [string]$Value)
    if ($DryRun) {
        Write-Host "[DRY RUN] Would set secret $Name = $Value"
        return
    }
    $Value | gh secret set $Name --repo $Repo
    Write-Host "Secret $Name updated."
}

function Trigger-Deploy {
    if ($DryRun) {
        Write-Host "[DRY RUN] Would trigger workflow_dispatch for Deploy"
        return
    }
    gh workflow run deploy.yml --repo $Repo
    Write-Host "Deploy workflow triggered. Monitor at: https://github.com/$Repo/actions"
}

# --- Main ---

Write-Host "=== Fix Prod API URL ===" -ForegroundColor Cyan

# 1. Ensure gh CLI
if (-not (Test-GhCli)) {
    Install-GhCli
    if (-not (Test-GhCli)) {
        Write-Error "gh CLI still not available after install. Restart terminal and retry."
        exit 1
    }
}

# 2. Ensure auth
if (-not (Test-GhAuth)) {
    Write-Host "`nGitHub CLI is not authenticated." -ForegroundColor Yellow
    Write-Host "Run this command manually, then re-run this script:"
    Write-Host "    gh auth login`n" -ForegroundColor Cyan
    exit 1
}

Write-Host "Authenticated to GitHub. Proceeding..." -ForegroundColor Green

# 3. Set the secret (always set — we can't read the current value)
Write-Host "Setting VITE_API_BASE_URL to $TargetUrl ..."
Set-GhSecret -Name "VITE_API_BASE_URL" -Value $TargetUrl

# 4. Also ensure PROD_API_BASE_URL is set (used by smoke tests)
Write-Host "Setting PROD_API_BASE_URL to $TargetUrl ..."
Set-GhSecret -Name "PROD_API_BASE_URL" -Value $TargetUrl

# 5. Trigger deploy
Write-Host "Triggering Deploy workflow..."
Trigger-Deploy

Write-Host "`nDone. The next deploy will bake the correct API URL into the frontend build." -ForegroundColor Green
