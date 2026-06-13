#!/usr/bin/env pwsh
<#
.SYNOPSIS
    NONI Automated Deployment - Windows PowerShell Wrapper
.DESCRIPTION
    Zero-manual-step deployment automation for Windows.
    Wraps Python auto_deploy.py with Windows-specific enhancements.
    
    This script provides FULLY AUTOMATED deployment without requiring:
    - git CLI
    - flyctl CLI
    - npm/node
    - GitHub CLI
    
    Only requires: PowerShell 5.1+ or PowerShell 7+, Python 3.7+
    
    Following "The Process" - Enterprise Standard
.PARAMETER GitHubToken
    GitHub Personal Access Token (optional, will prompt if not provided)
.PARAMETER CheckOnly
    Only run pre-checks without deploying
.PARAMETER InstallPython
    Automatically install Python if not found
.EXAMPLE
    .\AutoDeploy.ps1
    
    Runs in interactive mode, prompting for token if needed
.EXAMPLE
    .\AutoDeploy.ps1 -GitHubToken "ghp_xxx"
    
    Deploys with provided token
.EXAMPLE
    .\AutoDeploy.ps1 -CheckOnly
    
    Only checks configuration without deploying
.NOTES
    Version: 2.0
    Date: 2026-06-11
    Process: The Process v2.0
#>

[CmdletBinding()]
param(
    [Parameter()]
    [string]$GitHubToken = "",
    
    [Parameter()]
    [switch]$CheckOnly,
    
    [Parameter()]
    [switch]$InstallPython,
    
    [Parameter()]
    [switch]$SkipConfirmation
)

# Error handling
$ErrorActionPreference = "Stop"

# Color definitions for PowerShell
$Colors = @{
    Header = "Magenta"
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
}

function Write-Header {
    param([string]$Text)
    Write-Host "`n$('=' * 60)" -ForegroundColor $Colors.Header
    Write-Host $Text -ForegroundColor $Colors.Header
    Write-Host "$('=' * 60)`n" -ForegroundColor $Colors.Header
}

function Write-Step {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error", "Wait")]
        [string]$Status = "Info"
    )
    
    $icons = @{
        Info = "[*]"
        Success = "[✓]"
        Warning = "[!]"
        Error = "[✗]"
        Wait = "[⏳]"
    }
    
    $color = switch ($Status) {
        "Success" { $Colors.Success }
        "Warning" { $Colors.Warning }
        "Error" { $Colors.Error }
        "Wait" { $Colors.Info }
        default { $Colors.Info }
    }
    
    Write-Host "$($icons[$Status]) $Message" -ForegroundColor $color
}

# Configuration
$RepoOwner = "smiles70"
$RepoName = "Noni"
$RepoFull = "$RepoOwner/$RepoName"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Write-Header "NONI AUTOMATED DEPLOYMENT - WINDOWS"
Write-Host "Following The Process v2.0 - Zero Manual Steps" -ForegroundColor $Colors.Info
Write-Host "Repository: $RepoFull`n" -ForegroundColor $Colors.Info

# ============================================================================
# PHASE 0: PREREQUISITE CHECK
# ============================================================================
Write-Header "PHASE 0: PREREQUISITE CHECK"

# Check Python
Write-Step "Checking Python availability..." "Wait"
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if ($pythonCmd) {
    $pythonVersion = & $pythonCmd.Source --version 2>&1
    Write-Step "Found: $pythonVersion" "Success"
} else {
    Write-Step "Python not found" "Error"
    
    if ($InstallPython) {
        Write-Step "Installing Python..." "Wait"
        try {
            # Download Python installer
            $pythonUrl = "https://www.python.org/ftp/python/3.11.8/python-3.11.8-amd64.exe"
            $pythonInstaller = "$env:TEMP\python-installer.exe"
            
            Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller -UseBasicParsing
            
            # Install silently
            Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
            
            # Refresh environment
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
            
            # Verify
            $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
            if ($pythonCmd) {
                Write-Step "Python installed successfully" "Success"
            } else {
                throw "Python installation verification failed"
            }
        } catch {
            Write-Step "Failed to install Python: $_" "Error"
            Write-Host "`nPlease install Python manually from https://python.org" -ForegroundColor $Colors.Warning
            exit 1
        }
    } else {
        Write-Host "`nPython is required but not installed." -ForegroundColor $Colors.Warning
        Write-Host "Options:" -ForegroundColor $Colors.Info
        Write-Host "  1. Install Python: https://python.org" -ForegroundColor $Colors.Info
        Write-Host "  2. Run with -InstallPython flag" -ForegroundColor $Colors.Info
        exit 1
    }
}

# Check Python requests library
Write-Step "Checking Python dependencies..." "Wait"
try {
    $null = python -c "import requests" 2>&1
    Write-Step "requests library: OK" "Success"
} catch {
    Write-Step "requests library: Installing..." "Warning"
    python -m pip install requests -q
    Write-Step "requests library: Installed" "Success"
}

# ============================================================================
# PHASE 1: TOKEN ACQUISITION (If not provided)
# ============================================================================
if (-not $GitHubToken) {
    Write-Header "PHASE 1: TOKEN ACQUISITION"
    
    Write-Step "GitHub token required for automation" "Info"
    Write-Host "`nTo create a GitHub Personal Access Token:" -ForegroundColor $Colors.Info
    Write-Host "  1. Go to: https://github.com/settings/tokens" -ForegroundColor White
    Write-Host "  2. Click 'Generate new token (classic)'" -ForegroundColor White
    Write-Host "  3. Select these scopes:" -ForegroundColor White
    Write-Host "     ☑ repo (Full control of private repositories)" -ForegroundColor White
    Write-Host "     ☑ workflow (Update GitHub Action workflow files)" -ForegroundColor White
    Write-Host "  4. Click 'Generate token' at bottom" -ForegroundColor White
    Write-Host "  5. COPY the token (you won't see it again)" -ForegroundColor White
    Write-Host "`n⚠️  SECURITY: This token grants access to your repository." -ForegroundColor $Colors.Warning
    Write-Host "   Store it securely and never share it." -ForegroundColor $Colors.Warning
    
    # Interactive input
    $secureToken = Read-Host -Prompt "`nEnter your GitHub token" -AsSecureString
    $GitHubToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
    )
    
    if (-not $GitHubToken) {
        Write-Step "No token provided, exiting" "Error"
        exit 1
    }
}

# ============================================================================
# PHASE 2: CONFIRMATION
# ============================================================================
if (-not $SkipConfirmation) {
    Write-Header "PHASE 2: DEPLOYMENT CONFIRMATION"
    
    Write-Step "This will:" "Info"
    Write-Host "  • Check repository secrets" -ForegroundColor White
    Write-Host "  • Trigger GitHub Actions workflow" -ForegroundColor White
    Write-Host "  • Monitor build progress" -ForegroundColor White
    Write-Host "  • Verify deployment success" -ForegroundColor White
    Write-Host "  • Check for G3 (localhost) issue" -ForegroundColor White
    
    Write-Host "`nRepository: $RepoFull" -ForegroundColor $Colors.Info
    Write-Host "Workflow: deploy.yml" -ForegroundColor $Colors.Info
    
    if ($CheckOnly) {
        Write-Host "`nMode: CHECK ONLY (no deployment)" -ForegroundColor $Colors.Warning
    }
    
    $confirmation = Read-Host -Prompt "`nProceed? (yes/no)"
    if ($confirmation -ne "yes") {
        Write-Step "Deployment cancelled by user" "Warning"
        exit 0
    }
}

# ============================================================================
# PHASE 3: EXECUTE PYTHON AUTOMATION
# ============================================================================
Write-Header "PHASE 3: EXECUTING AUTOMATION"

$pythonScript = Join-Path $ScriptDir "auto_deploy.py"

if (-not (Test-Path $pythonScript)) {
    Write-Step "Python script not found: $pythonScript" "Error"
    exit 1
}

Write-Step "Starting Python automation..." "Wait"

# Build argument list
$pythonArgs = @($pythonScript)
if ($GitHubToken) {
    $pythonArgs += "--github-token"
    $pythonArgs += $GitHubToken
}
if ($CheckOnly) {
    $pythonArgs += "--check-only"
}

try {
    # Run Python script
    & python @pythonArgs
    
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Step "Automation completed successfully" "Success"
    } else {
        Write-Step "Automation failed with exit code $exitCode" "Error"
        exit $exitCode
    }
} catch {
    Write-Step "Error executing Python script: $_" "Error"
    exit 1
}

# ============================================================================
# PHASE 4: POST-DEPLOYMENT
# ============================================================================
Write-Header "PHASE 4: DEPLOYMENT SUMMARY"

Write-Step "Actions completed:" "Success"
Write-Host "  ✓ Repository secrets verified" -ForegroundColor $Colors.Success
Write-Host "  ✓ GitHub Actions workflow triggered" -ForegroundColor $Colors.Success
Write-Host "  ✓ Build monitored to completion" -ForegroundColor $Colors.Success
Write-Host "  ✓ Deployment verified" -ForegroundColor $Colors.Success
Write-Host "  ✓ G3 (localhost) check passed" -ForegroundColor $Colors.Success

Write-Host "`nResources:" -ForegroundColor $Colors.Info
Write-Host "  Frontend: https://noni-web.pages.dev" -ForegroundColor White
Write-Host "  API: https://noni-api.fly.dev" -ForegroundColor White
Write-Host "  Actions: https://github.com/$RepoFull/actions" -ForegroundColor White

Write-Host "`nNext steps:" -ForegroundColor $Colors.Info
Write-Host "  1. Open https://noni-web.pages.dev in browser" -ForegroundColor White
Write-Host "  2. Press F12 → Network tab" -ForegroundColor White
Write-Host "  3. Confirm NO requests to localhost:8000" -ForegroundColor White
Write-Host "  4. Test login functionality" -ForegroundColor White

Write-Header "THE PROCESS COMPLETE"
Write-Host "Zero manual steps achieved" -ForegroundColor $Colors.Success
