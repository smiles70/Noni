---
title: Infrastructure Setup Guide
version: 2.0
date: 2026-06-11
process: The Process v2.0
---

# Infrastructure Setup Guide

Complete automated setup for Noni project infrastructure using **The Process** methodology.

## Quick Start

```powershell
# Run the automated setup script
.\scripts\setup-infrastructure.ps1

# Or with specific tokens
.\scripts\setup-infrastructure.ps1 -GitHubToken "ghp_xxx" -FlyToken "fly_xxx"
```

## Prerequisites

- Windows 10/11 or Windows Server 2019+
- PowerShell 7+ (install from Microsoft Store or https://github.com/PowerShell/PowerShell)
- Administrator privileges (for some installations)
- Internet connection

## Required Accounts

Before starting, ensure you have access to:

| Service | URL | Purpose |
|---------|-----|---------|
| GitHub | https://github.com/smiles70/Noni | Repository access |
| Fly.io | https://fly.io/apps/noni-api | Backend deployment |
| Cloudflare | https://dash.cloudflare.com | Frontend deployment |
| Clerk | https://dashboard.clerk.com | Authentication |
| Supabase | https://app.supabase.com | Database |

## The Process: Infrastructure Setup

### Phase 0: Session State Open

**Agent:** Session State  
**Action:** Assess current infrastructure state

```powershell
# Check current tool availability
Get-Command git, flyctl, npm, node, gh -ErrorAction SilentlyContinue
```

**Expected Output:**
- ✓ Git: version 2.x
- ✓ Fly.io CLI: version 0.x
- ✓ npm: version 10.x
- ✓ Node.js: version 20.x
- ✓ GitHub CLI: version 2.x

### Phase 1: Tool Installation

**Agent:** Infrastructure  
**Action:** Install missing tools

#### Option A: Automated (Recommended)

```powershell
.\scripts\setup-infrastructure.ps1
```

The script will:
1. Detect installed tools
2. Download missing tools
3. Install to appropriate locations
4. Configure PATH

#### Option B: Manual Installation

**Git:**
```powershell
# Download from https://git-scm.com/download/win
# Run installer with defaults
```

**Fly.io CLI:**
```powershell
# PowerShell (Run as Administrator)
iwr https://fly.io/install.ps1 -useb | iex
```

**Node.js (includes npm):**
```powershell
# Download from https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi
# Or use nvm-windows: https://github.com/coreybutler/nvm-windows
```

**GitHub CLI:**
```powershell
# Download from https://cli.github.com/
# Or use winget:
winget install --id GitHub.cli
```

### Phase 2: Authentication Setup

**Agent:** Security  
**Action:** Configure authentication tokens

#### GitHub Authentication

```powershell
# Using GitHub CLI
gh auth login

# Or with token
gh auth login --with-token < my-token.txt
```

**Required Scopes:** `repo`, `workflow`

#### Fly.io Authentication

```powershell
# Get token from https://fly.io/user/personal_access_tokens
flyctl auth token

# Or login interactively
flyctl auth login
```

### Phase 3: Repository Secrets Configuration

**Agent:** GitHub Agent  
**Action:** Configure repository secrets for CI/CD

**Required Secrets:**

| Secret | Value Source | Purpose |
|--------|--------------|---------|
| `VITE_API_BASE_URL` | `https://noni-api.fly.dev` | Frontend API URL |
| `VITE_CLERK_PUBLISHABLE_KEY` | Clerk Dashboard → API Keys | Frontend auth |
| `CLERK_JWKS_URL` | Clerk Dashboard → JWT | Backend auth |
| `FLY_API_TOKEN` | `flyctl auth token` | Fly.io deployment |
| `SUPABASE_ACCESS_TOKEN` | Supabase Dashboard | Database |
| `SUPABASE_DB_PASSWORD` | Supabase Settings | Database password |
| `SUPABASE_PROJECT_ID` | Supabase URL | Database ID |
| `CLOUDFLARE_API_TOKEN` | Cloudflare API Tokens | Frontend deployment |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard | Account ID |

**Automated Configuration:**

```powershell
# Run with GitHub token to auto-configure
.\scripts\setup-infrastructure.ps1 -GitHubToken "ghp_xxx"
```

**Manual Configuration:**

1. Go to `https://github.com/smiles70/Noni/settings/secrets/actions`
2. Click "New repository secret" for each secret above
3. Paste the value
4. Click "Add secret"

### Phase 4: Deployment

**Agent:** Deploy  
**Action:** Execute full deployment

#### Full Deploy (Backend + Frontend)

```powershell
# Via GitHub Actions (recommended)
gh workflow run deploy.yml --repo smiles70/Noni

# Or via web interface
# https://github.com/smiles70/Noni/actions/workflows/deploy.yml
```

#### Frontend-Only Deploy (When Backend is Healthy)

```powershell
# Option 1: GitHub Actions with skip flag
# Modify deploy.yml to add 'skip-backend' input

# Option 2: Direct Cloudflare Pages deploy
# Use Cloudflare dashboard or wrangler CLI
```

### Phase 5: Verification

**Agent:** Audit  
**Action:** Verify deployment success

```powershell
# Backend health check
curl https://noni-api.fly.dev/health

# Auth endpoint check
curl https://noni-api.fly.dev/api/v1/auth/config

# Frontend check (no localhost references)
curl -s https://noni-web.pages.dev/ | findstr "localhost"
# Should return NOTHING

# Browser verification
# Open https://noni-web.pages.dev, check Network tab for localhost:8000
```

## Troubleshooting

### Issue: GitHub Actions workflow fails

**Diagnosis:**
```powershell
# Check workflow logs
gh run list --repo smiles70/Noni
gh run view <run-id> --repo smiles70/Noni
```

**Common Causes:**
1. Missing repository secret
2. Invalid token permissions
3. Fly.io app not found
4. Supabase connection failure

### Issue: flyctl not found after installation

**Fix:**
```powershell
# Add to PATH manually
$env:PATH += ";$env:USERPROFILE\.fly\bin"

# Or for permanent addition
[Environment]::SetEnvironmentVariable(
    "PATH",
    "$env:PATH;$env:USERPROFILE\.fly\bin",
    "User"
)
```

### Issue: G3 Login Loop After Deploy

**Diagnosis:**
```powershell
# Check if localhost is in bundle
curl -s https://noni-web.pages.dev/assets/*.js | findstr "localhost"
```

**Fix:**
1. Verify `VITE_API_BASE_URL` secret is set correctly
2. Re-run Deploy workflow
3. Check build logs for verification script output

## G3 Prevention System

The following safeguards are now in place:

### Layer 1: Pre-Build Verification
- **Script:** `frontend/scripts/verify-build-env.mjs`
- **Checks:** VITE_API_BASE_URL set, no localhost, HTTPS required
- **Trigger:** Runs automatically before `npm run build`

### Layer 2: Build Process
- **Tool:** Vite + TypeScript
- **Behavior:** Inlines environment variables at build time

### Layer 3: Post-Build Verification
- **Script:** `frontend/scripts/verify-bundle.mjs`
- **Checks:** Scans bundle for localhost references
- **Trigger:** Runs automatically after `npm run build`

### Layer 4: CI/CD Integration
- **File:** `.github/workflows/deploy.yml`
- **Behavior:** Fails deployment if any verification fails

## Maintenance

### Updating Tools

```powershell
# Update Fly.io CLI
flyctl version update

# Update Node.js (if using nvm-windows)
nvm install latest
nvm use latest

# Update GitHub CLI
gh extension upgrade --all
```

### Rotating Secrets

1. Generate new token at provider dashboard
2. Update in GitHub: `https://github.com/smiles70/Noni/settings/secrets/actions`
3. Re-run Deploy workflow

## Reference

### File Locations

| File | Purpose |
|------|---------|
| `scripts/setup-infrastructure.ps1` | Automated setup script |
| `docs/gotchas.md` | Known issues and prevention |
| `.github/workflows/deploy.yml` | CI/CD pipeline |
| `frontend/scripts/verify-build-env.mjs` | Pre-build guard |
| `frontend/scripts/verify-bundle.mjs` | Post-build guard |

### External Documentation

- Fly.io: https://fly.io/docs/
- GitHub Actions: https://docs.github.com/en/actions
- Cloudflare Pages: https://developers.cloudflare.com/pages/
- Clerk: https://clerk.com/docs
- Supabase: https://supabase.com/docs

---

**The Process Version:** 2.0  
**Last Updated:** 2026-06-11  
**Status:** Active and maintained
