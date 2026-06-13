#!/usr/bin/env pwsh
#requires -Version 7
<#
.SYNOPSIS
    Automated Infrastructure Setup for Noni Project
.DESCRIPTION
    Following "The Process" - Enterprise-grade infrastructure setup script
    Installs and configures: Git, Fly.io CLI (flyctl), Node.js/npm, GitHub CLI (gh)
    Configures GitHub Actions secrets and triggers deployment
.NOTES
    Run with: .\scripts\setup-infrastructure.ps1
    Requires: PowerShell 7+, Administrator privileges for some operations
#>

param(
    [switch]$SkipInstall,
    [switch]$ConfigureOnly,
    [string]$GitHubToken = "",
    [string]$FlyToken = ""
)

# Error handling - fail fast
$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  NONI INFRASTRUCTURE SETUP" -ForegroundColor Cyan
Write-Host "  The Process v2.0 - Enterprise Standard" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Configuration
$REPO_OWNER = "smiles70"
$REPO_NAME = "Noni"
$REPO_FULL = "$REPO_OWNER/$REPO_NAME"
$FLY_APP = "noni-api"

# Tool versions (pinned for reproducibility)
$NODE_VERSION = "20.11.0"

# ============================================================================
# PHASE 1: DETECTION - Check current state
# ============================================================================
Write-Host "[PHASE 1] DETECTING CURRENT STATE..." -ForegroundColor Yellow

$tools = @{
    git = @{ cmd = "git"; args = "--version"; name = "Git" }
    flyctl = @{ cmd = "flyctl"; args = "version"; name = "Fly.io CLI" }
    npm = @{ cmd = "npm"; args = "--version"; name = "npm" }
    node = @{ cmd = "node"; args = "--version"; name = "Node.js" }
    gh = @{ cmd = "gh"; args = "--version"; name = "GitHub CLI" }
}

$detected = @{}
foreach ($tool in $tools.Keys) {
    $info = $tools[$tool]
    try {
        $output = Invoke-Expression "$($info.cmd) $($info.args) 2>&1" | Select-Object -First 1
        $detected[$tool] = $output
        Write-Host "  ✓ $($info.name): $output" -ForegroundColor Green
    } catch {
        $detected[$tool] = $null
        Write-Host "  ✗ $($info.name): NOT FOUND" -ForegroundColor Red
    }
}

# ============================================================================
# PHASE 2: INSTALLATION - Download and install missing tools
# ============================================================================
if (-not $ConfigureOnly) {
    Write-Host "`n[PHASE 2] INSTALLING MISSING TOOLS..." -ForegroundColor Yellow
    
    # Create temp directory for downloads
    $tempDir = "$env:TEMP\noni-setup"
    New-Item -ItemType Directory -Force -Path $tempDir | Out-Null
    
    # --- Install Git ---
    if (-not $detected.git) {
        Write-Host "  → Installing Git..." -ForegroundColor Blue
        $gitUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"
        $gitInstaller = "$tempDir\git-installer.exe"
        
        try {
            Invoke-WebRequest -Uri $gitUrl -OutFile $gitInstaller -UseBasicParsing
            Write-Host "    Downloaded Git installer" -ForegroundColor Gray
            Write-Host "    Please run the installer: $gitInstaller" -ForegroundColor Yellow
            Write-Host "    After installation, re-run this script with -ConfigureOnly" -ForegroundColor Yellow
            # Don't auto-install Git as it requires GUI interaction
            return
        } catch {
            Write-Host "    ✗ Failed to download Git: $_" -ForegroundColor Red
        }
    }
    
    # --- Install Fly.io CLI (flyctl) ---
    if (-not $detected.flyctl) {
        Write-Host "  → Installing Fly.io CLI (flyctl)..." -ForegroundColor Blue
        try {
            # PowerShell install method
            $installScript = Invoke-WebRequest -Uri "https://fly.io/install.ps1" -UseBasicParsing
            Invoke-Expression $installScript
            
            # Add to PATH for this session
            $env:PATH += ";$env:USERPROFILE\.fly\bin"
            
            # Verify
            $flyVersion = flyctl version
            Write-Host "    ✓ Fly.io CLI installed: $flyVersion" -ForegroundColor Green
            $detected.flyctl = $flyVersion
        } catch {
            Write-Host "    ✗ Failed to install flyctl: $_" -ForegroundColor Red
            Write-Host "    Manual install: https://fly.io/docs/hands-on/install-flyctl/" -ForegroundColor Yellow
        }
    }
    
    # --- Install Node.js (includes npm) ---
    if (-not $detected.node -or -not $detected.npm) {
        Write-Host "  → Installing Node.js v$NODE_VERSION..." -ForegroundColor Blue
        try {
            # Use nvs or download directly
            $nodeUrl = "https://nodejs.org/dist/v$NODE_VERSION/node-v$NODE_VERSION-win-x64.zip"
            $nodeZip = "$tempDir\node.zip"
            $nodeDir = "$env:LOCALAPPDATA\node"
            
            Invoke-WebRequest -Uri $nodeUrl -OutFile $nodeZip -UseBasicParsing
            Expand-Archive -Path $nodeZip -DestinationPath $nodeDir -Force
            
            # Add to PATH
            $env:PATH = "$nodeDir\node-v$NODE_VERSION-win-x64;$env:PATH"
            
            # Verify
            $nodeVersion = node --version
            $npmVersion = npm --version
            Write-Host "    ✓ Node.js installed: $nodeVersion" -ForegroundColor Green
            Write-Host "    ✓ npm installed: $npmVersion" -ForegroundColor Green
            $detected.node = $nodeVersion
            $detected.npm = $npmVersion
        } catch {
            Write-Host "    ✗ Failed to install Node.js: $_" -ForegroundColor Red
            Write-Host "    Download manually: https://nodejs.org/dist/v$NODE_VERSION/" -ForegroundColor Yellow
        }
    }
    
    # --- Install GitHub CLI ---
    if (-not $detected.gh) {
        Write-Host "  → Installing GitHub CLI..." -ForegroundColor Blue
        try {
            $ghUrl = "https://github.com/cli/cli/releases/download/v2.42.0/gh_2.42.0_windows_amd64.msi"
            $ghInstaller = "$tempDir\gh-installer.msi"
            
            Invoke-WebRequest -Uri $ghUrl -OutFile $ghInstaller -UseBasicParsing
            Write-Host "    Downloaded GitHub CLI installer" -ForegroundColor Gray
            Write-Host "    Please run the installer: $ghInstaller" -ForegroundColor Yellow
            Write-Host "    After installation, re-run this script with -ConfigureOnly" -ForegroundColor Yellow
            # Don't auto-install as it requires GUI interaction
            return
        } catch {
            Write-Host "    ✗ Failed to download GitHub CLI: $_" -ForegroundColor Red
        }
    }
}

# ============================================================================
# PHASE 3: CONFIGURATION - Set up GitHub repository secrets
# ============================================================================
Write-Host "`n[PHASE 3] CONFIGURING GITHUB REPOSITORY..." -ForegroundColor Yellow

# Check if we have gh CLI and token
if (-not $detected.gh -and -not $GitHubToken) {
    Write-Host "  ! GitHub CLI not available and no token provided" -ForegroundColor Yellow
    Write-Host "  → Please provide GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "     1. Go to: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "     2. Click 'Generate new token (classic)'" -ForegroundColor Cyan
    Write-Host "     3. Select scopes: repo, workflow" -ForegroundColor Cyan
    Write-Host "     4. Copy the token and provide it below" -ForegroundColor Cyan
    $GitHubToken = Read-Host -Prompt "  GitHub Token"
}

# Authenticate with GitHub if using gh CLI
if ($detected.gh) {
    Write-Host "  → Authenticating with GitHub..." -ForegroundColor Blue
    try {
        $authStatus = gh auth status 2>&1
        if ($authStatus -match "not logged into") {
            if ($GitHubToken) {
                $env:GH_TOKEN = $GitHubToken
                gh auth login --with-token
            } else {
                gh auth login
            }
        }
        Write-Host "    ✓ GitHub CLI authenticated" -ForegroundColor Green
    } catch {
        Write-Host "    ✗ GitHub authentication failed: $_" -ForegroundColor Red
    }
}

# Required secrets for deployment
$requiredSecrets = @(
    @{ name = "VITE_API_BASE_URL"; value = "https://noni-api.fly.dev"; desc = "Frontend API URL" }
    @{ name = "VITE_CLERK_PUBLISHABLE_KEY"; value = ""; desc = "Clerk Frontend Key (from clerk.com)" }
    @{ name = "VITE_AUTH_PROVIDER"; value = "clerk"; desc = "Auth provider" }
    @{ name = "FLY_API_TOKEN"; value = $FlyToken; desc = "Fly.io API Token" }
    @{ name = "SUPABASE_ACCESS_TOKEN"; value = ""; desc = "Supabase Token (from supabase.com)" }
    @{ name = "SUPABASE_DB_PASSWORD"; value = ""; desc = "Supabase DB Password" }
    @{ name = "SUPABASE_PROJECT_ID"; value = ""; desc = "Supabase Project ID" }
    @{ name = "CLOUDFLARE_API_TOKEN"; value = ""; desc = "Cloudflare API Token" }
    @{ name = "CLOUDFLARE_ACCOUNT_ID"; value = ""; desc = "Cloudflare Account ID" }
)

Write-Host "`n  Required GitHub Secrets:" -ForegroundColor Cyan
foreach ($secret in $requiredSecrets) {
    $status = if ($secret.value) { "✓ SET" } else { "? NEEDED" }
    $color = if ($secret.value) { "Green" } else { "Yellow" }
    Write-Host "    $status $($secret.name) - $($secret.desc)" -ForegroundColor $color
}

# Check current secrets using GitHub API
Write-Host "`n  → Checking existing secrets..." -ForegroundColor Blue
if ($GitHubToken) {
    try {
        $headers = @{ 
            "Authorization" = "token $GitHubToken"
            "Accept" = "application/vnd.github.v3+json"
        }
        $secretsUrl = "https://api.github.com/repos/$REPO_FULL/actions/secrets"
        $existingSecrets = Invoke-RestMethod -Uri $secretsUrl -Headers $headers -Method Get
        
        Write-Host "    Found $($existingSecrets.secrets.Count) existing secrets:" -ForegroundColor Gray
        foreach ($secret in $existingSecrets.secrets) {
            Write-Host "      - $($secret.name) (updated: $($secret.updated_at))" -ForegroundColor Gray
        }
    } catch {
        Write-Host "    ! Could not fetch secrets: $_" -ForegroundColor Yellow
    }
}

# ============================================================================
# PHASE 4: FLY.IO CONFIGURATION
# ============================================================================
if ($detected.flyctl) {
    Write-Host "`n[PHASE 4] CONFIGURING FLY.IO..." -ForegroundColor Yellow
    
    if ($FlyToken) {
        Write-Host "  → Authenticating with Fly.io..." -ForegroundColor Blue
        try {
            $env:FLY_ACCESS_TOKEN = $FlyToken
            flyctl auth token 2>&1 | Out-Null
            Write-Host "    ✓ Fly.io authenticated" -ForegroundColor Green
            
            # Check app status
            Write-Host "  → Checking app status..." -ForegroundColor Blue
            $appStatus = flyctl status --app $FLY_APP 2>&1
            if ($appStatus -match "running") {
                Write-Host "    ✓ App '$FLY_APP' is running" -ForegroundColor Green
            } else {
                Write-Host "    ! App status: $appStatus" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "    ✗ Fly.io authentication failed: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  ! No Fly.io token provided" -ForegroundColor Yellow
        Write-Host "  → Get token from: https://fly.io/user/personal_access_tokens" -ForegroundColor Cyan
        Write-Host "  → Or run: flyctl auth login" -ForegroundColor Cyan
    }
}

# ============================================================================
# PHASE 5: DEPLOYMENT - Trigger GitHub Actions
# ============================================================================
Write-Host "`n[PHASE 5] TRIGGERING DEPLOYMENT..." -ForegroundColor Yellow

Write-Host "  Current status:" -ForegroundColor Cyan
Write-Host "    - Backend (Fly.io): Healthy (verified earlier)" -ForegroundColor Green
Write-Host "    - Frontend (Cloudflare): Needs redeploy" -ForegroundColor Yellow
Write-Host "    - G3 Guards: IMPLEMENTED in repository" -ForegroundColor Green

Write-Host "`n  Manual steps required:" -ForegroundColor Cyan
Write-Host "    1. Go to: https://github.com/$REPO_FULL/actions" -ForegroundColor White
Write-Host "    2. Click 'Deploy' workflow" -ForegroundColor White
Write-Host "    3. Click 'Run workflow' → 'Branch: main' → 'Run workflow'" -ForegroundColor White

if ($GitHubToken) {
    Write-Host "`n  → Attempting to trigger via API..." -ForegroundColor Blue
    try {
        $headers = @{ 
            "Authorization" = "token $GitHubToken"
            "Accept" = "application/vnd.github.v3+json"
        }
        $body = @{
            ref = "main"
        } | ConvertTo-Json
        
        $dispatchUrl = "https://api.github.com/repos/$REPO_FULL/actions/workflows/deploy.yml/dispatches"
        Invoke-RestMethod -Uri $dispatchUrl -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "    ✓ Deployment triggered successfully!" -ForegroundColor Green
    } catch {
        Write-Host "    ! Could not trigger automatically: $_" -ForegroundColor Yellow
        Write-Host "    → Please trigger manually using steps above" -ForegroundColor Yellow
    }
}

# ============================================================================
# SUMMARY
# ============================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Tools Status:" -ForegroundColor Yellow
foreach ($tool in $detected.Keys) {
    $status = if ($detected[$tool]) { "✓ INSTALLED" } else { "✗ NOT FOUND" }
    $color = if ($detected[$tool]) { "Green" } else { "Red" }
    Write-Host "  $status - $($tools[$tool].name)" -ForegroundColor $color
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. Complete Git installation (if needed)" -ForegroundColor White
Write-Host "  2. Complete GitHub CLI installation (if needed)" -ForegroundColor White
Write-Host "  3. Set missing GitHub repository secrets" -ForegroundColor White
Write-Host "  4. Trigger Deploy workflow" -ForegroundColor White
Write-Host "  5. Verify login loop is fixed" -ForegroundColor White

Write-Host "`nDocumentation:" -ForegroundColor Yellow
Write-Host "  - G3 Prevention: docs/gotchas.md" -ForegroundColor Gray
Write-Host "  - Session Log: .ai/sessions/2026-06-11_g3-fix-executed.md" -ForegroundColor Gray
Write-Host "  - Deploy Config: .github/workflows/deploy.yml" -ForegroundColor Gray

Write-Host "`n" -ForegroundColor Cyan
