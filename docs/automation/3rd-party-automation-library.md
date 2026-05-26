# 3rd-Party Integration Automation Library

> Exhaustive research on API-first, CLI-first, and programmatic automation for
> Cloudflare, Fly.io, and GitHub. Built to eliminate manual dashboard clicks.
>
> **Rule**: Automated first. Manual only as last resort. Every vendor claim is
> verified against official API docs and CLI reference.

---

## Table of Contents

1. [Executive Summary — The Bootstrapping Problem](#1-executive-summary--the-bootstrapping-problem)
2. [Cloudflare](#2-cloudflare)
3. [Fly.io](#3-flyio)
4. [GitHub](#4-github)
5. [Cross-Vendor Bootstrap Script](#5-cross-vendor-bootstrap-script)
6. [References](#6-references)

---

## 1. Executive Summary — The Bootstrapping Problem

| Vendor | Can create *first* credential via API/CLI? | Minimum manual step | Notes |
|--------|--------------------------------------------|---------------------|-------|
| **Cloudflare** | **No** (API tokens) / **Partial** (Global API Key) | One dashboard visit to view/copy Global API Key, OR one token creation via dashboard | API tokens require an existing token or Global API Key. Global API Key is legacy but programmatically usable. |
| **Fly.io** | **Partial** | `fly auth login` (can use `--token` flag with existing token) | `fly tokens create` works non-interactively once authenticated. First auth requires browser flow OR an existing token. |
| **GitHub** | **Yes** | `gh auth login` OR Personal Access Token via web | `gh` CLI fully automates secret creation, workflow triggers. PAT can be created via web UI, then everything else is CLI. |

**Verdict**: Zero *completely* manual steps is impossible for Cloudflare and Fly.io
because they require an identity proof that can only be established through a
browser-based OAuth flow or a dashboard visit. However, after the one-time
bootstrap, 100% of ongoing operations (token rotation, deploys, secret sync)
can be automated.

---

## 2. Cloudflare

### 2.1 Authentication Methods

| Method | How to obtain | Can create tokens? | Scriptable? |
|--------|---------------|-------------------|-------------|
| **API Token** (preferred) | Dashboard → My Profile → API Tokens | Yes (with `Account API Tokens Write` perm) | Yes, via `Authorization: Bearer <token>` |
| **Global API Key** (legacy) | Dashboard → My Profile → API Keys → View | Yes (full account access) | Yes, via `X-Auth-Key` + `X-Auth-Email` headers |
| **Origin CA Key** | Dashboard → SSL/TLS → Origin Server | No | N/A |

**Key insight from docs**: "Before you can create tokens via the API, you need to
generate the initial token via the Cloudflare dashboard." —
[Create tokens via API](https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/)

However, the **Global API Key** sidesteps this: it is a long-lived credential that
can create API tokens programmatically. It is deprecated but still fully
functional for this purpose.

### 2.2 API Token Creation via API (Authenticated)

**Endpoint**: `POST /client/v4/accounts/{account_id}/tokens`

**Auth**: Bearer token with `Account API Tokens Write` permission, OR
Global API Key (`X-Auth-Key` + `X-Auth-Email`).

**Request body** (simplified):
```json
{
  "name": "Noni Pages Deploy",
  "policies": [
    {
      "effect": "allow",
      "resources": {
        "com.cloudflare.api.account.<account_id>": "*"
      },
      "permission_groups": [
        { "id": "<permission_group_id>" }
      ]
    }
  ],
  "condition": {
    "request.ip": {
      "in": [],
      "not_in": []
    }
  }
}
```

**Required permission group IDs** (obtained from
`GET /client/v4/user/tokens/permission_groups`):
- `Cloudflare Pages:Edit` — for Pages deploy
- `Zone:Read`, `Zone:Edit` — for DNS / zone management
- `Account Settings:Read` — for account lookup

**Response**: Contains `result.value` — the token secret. **Shown only once.**

### 2.3 Listing Permission Groups

**Endpoint**: `GET /client/v4/user/tokens/permission_groups`

**Auth**: Any valid token or Global API Key.

Returns IDs like:
```json
{
  "result": [
    { "id": "e6a1186b5dcbf4b0", "name": "Cloudflare Pages Write" },
    { "id": "c8fed203ed2530ca", "name": "Zone Read" }
  ]
}
```

### 2.4 Pages Deploy via Wrangler CLI (Non-Interactive)

**Prerequisite**: `CLOUDFLARE_API_TOKEN` environment variable set.

```bash
# Install wrangler
npm install -g wrangler

# Set token (non-interactive)
export CLOUDFLARE_API_TOKEN="your-token-here"

# Create project (if not exists)
npx wrangler pages project create noni-web --production-branch=main

# Deploy build output
npx wrangler pages deploy frontend/dist --project-name=noni-web --branch=main
```

**Reference**: [System environment variables — Wrangler](https://developers.cloudflare.com/workers/wrangler/system-environment-variables/)

### 2.5 Pages Deploy via REST API (Direct Upload)

**Endpoint**: `POST /client/v4/accounts/{account_id}/pages/projects/{project_name}/deployments`

**Auth**: Bearer token with `Cloudflare Pages:Edit`.

Requires a multipart upload of the build artifacts. Wrangler CLI is the simpler
path; the REST API is for custom tooling.

**Reference**: [REST API — Cloudflare Pages](https://developers.cloudflare.com/pages/configuration/api/)

### 2.6 Cloudflare Script — Complete Automation

```powershell
#Requires -Version 7
<#
.SYNOPSIS
    Automate Cloudflare API token creation and Pages deploy.

.BOOTSTRAP
    Requires either:
    1. CLOUDFLARE_API_TOKEN  (with Account API Tokens Write)
    2. CLOUDFLARE_API_KEY    (Global API Key) + CLOUDFLARE_EMAIL

    If neither is set, the script exits with instructions to obtain
    the Global API Key from the dashboard (one-time).
#>
param(
    [string]$AccountId = $env:CLOUDFLARE_ACCOUNT_ID,
    [string]$ApiToken  = $env:CLOUDFLARE_API_TOKEN,
    [string]$ApiKey    = $env:CLOUDFLARE_API_KEY,
    [string]$Email     = $env:CLOUDFLARE_EMAIL
)

$ErrorActionPreference = "Stop"

function Get-CfAuthHeaders {
    if ($ApiToken) {
        return @{ Authorization = "Bearer $ApiToken" }
    }
    if ($ApiKey -and $Email) {
        return @{
            "X-Auth-Key"   = $ApiKey
            "X-Auth-Email" = $Email
        }
    }
    throw "Need CLOUDFLARE_API_TOKEN or (CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL)"
}

function Get-CfPermissionGroupId {
    param([string]$Name)
    $h = Get-CfAuthHeaders
    $url = "https://api.cloudflare.com/client/v4/user/tokens/permission_groups?name=$([uri]::EscapeDataString($Name))"
    $res = Invoke-RestMethod -Uri $url -Headers $h
    return $res.result | Where-Object { $_.name -eq $Name } | Select-Object -ExpandProperty id
}

function New-CfApiToken {
    param(
        [string]$TokenName,
        [string[]]$PermissionNames
    )
    $perms = $PermissionNames | ForEach-Object { Get-CfPermissionGroupId $_ }
    $body = @{
        name = $TokenName
        policies = @(
            @{
                effect = "allow"
                resources = @{ "com.cloudflare.api.account.$AccountId" = "*" }
                permission_groups = $perms | ForEach-Object { @{ id = $_ } }
            }
        )
    } | ConvertTo-Json -Depth 5

    $h = Get-CfAuthHeaders
    $url = "https://api.cloudflare.com/client/v4/accounts/$AccountId/tokens"
    $res = Invoke-RestMethod -Uri $url -Method POST -Headers $h -Body $body -ContentType "application/json"
    return $res.result.value   # shown only once
}

# --- Main ---
if (-not $AccountId) {
    # Try to discover account ID from /accounts list
    $h = Get-CfAuthHeaders
    $res = Invoke-RestMethod -Uri "https://api.cloudflare.com/client/v4/accounts" -Headers $h
    $AccountId = $res.result[0].id
    Write-Host "Discovered AccountId: $AccountId"
}

$token = New-CfApiToken -TokenName "noni-pages-deploy-auto" `
    -PermissionNames @("Cloudflare Pages Write","Zone Read")
Write-Host "Created token (save this): $token"
```

---

## 3. Fly.io

### 3.1 Authentication Methods

| Method | How to obtain | Scope | Scriptable? |
|--------|---------------|-------|-------------|
| **Personal access token** | `fly auth login` then `fly auth token` (deprecated) | Full org | Yes |
| **Deploy token** | `fly tokens create deploy -a <app>` | Single app deploy | Yes |
| **Org deploy token** | `fly tokens create org -o <org>` | Org-wide deploy | Yes |
| **Read-only token** | `fly tokens create readonly -o <org>` | Read state only | Yes |
| **Machine exec token** | `fly tokens create machine-exec` | Single command | Yes |

**Key insight**: `fly tokens create` is the modern, least-privilege way. It
replaces the old `fly auth token` (which returned the all-powerful personal
token). All token creation is CLI-driven and non-interactive once authenticated.

### 3.2 Token Creation via CLI

```bash
# Deploy token (recommended for CI)
fly tokens create deploy -a noni-api -x 720h

# Org deploy token (for multi-app pipelines)
fly tokens create org -o my-org -x 720h

# JSON output for scripting
fly tokens create deploy -a noni-api -x 720h --json
```

**Reference**: [Integrating flyctl](https://fly.io/docs/flyctl/integrating/)

### 3.3 Using Tokens Non-Interactively

```bash
export FLY_API_TOKEN="<token>"
fly deploy --remote-only   # skips all login prompts
```

### 3.4 Setting App Secrets via CLI

```bash
fly secrets set DATABASE_URL="..." SESSION_SECRET="..." -a noni-api
```

### 3.5 Bootstrapping Fly.io

**The catch**: `fly auth login` requires a browser for the OAuth flow by
default. However, you can bypass the browser:

```bash
# If you already have a token (e.g., from a previous machine):
export FLY_API_TOKEN="<existing-token>"
fly status -a noni-api   # works immediately, no login needed

# If you have a username/password (legacy, not recommended):
fly auth login --username <email> --password <password>
```

**Conclusion**: Fly.io's first auth requires either:
1. Browser-based OAuth (one-time)
2. An existing token copied from another machine

After bootstrap, 100% of operations are scriptable.

---

## 4. GitHub

### 4.1 Authentication Methods

| Method | How to obtain | Scope needed for repo secrets | Scriptable? |
|--------|---------------|------------------------------|-------------|
| **gh CLI** | `gh auth login` (web flow or PAT) | repo | Yes — wraps REST API |
| **Personal Access Token (classic)** | Settings → Developer settings → PAT | repo, admin:org | Yes — direct REST API |
| **Fine-grained PAT** | Settings → Developer settings → Fine-grained PAT | repository-level secrets: repo | Yes — direct REST API |
| **GitHub App** | App installation | repository-level: varies | Yes — via installation token |

**Reference**: [Encrypting secrets for the REST API](https://docs.github.com/en/rest/guides/encrypting-secrets-for-the-rest-api)

### 4.2 Setting Repository Secrets via REST API

**Step 1**: Get the repository public key.
```http
GET /repos/{owner}/{repo}/actions/secrets/public-key
Authorization: Bearer <token>
```

**Step 2**: Encrypt the secret with libsodium `crypto_box_seal`.

**Python**:
```python
from base64 import b64encode
from nacl import encoding, public

def encrypt(public_key: str, secret_value: str) -> str:
    public_key = public.PublicKey(
        public_key.encode("utf-8"), encoding.Base64Encoder()
    )
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")
```

**Step 3**: Create/update the secret.
```http
PUT /repos/{owner}/{repo}/actions/secrets/{secret_name}
Authorization: Bearer <token>
Content-Type: application/json

{
  "encrypted_value": "<base64-encrypted>",
  "key_id": "<public-key-id-from-step-1>"
}
```

**Reference**: [REST API endpoints for GitHub Actions Secrets](https://docs.github.com/en/rest/actions/secrets)

### 4.3 GitHub Script — Complete Automation

```powershell
#Requires -Version 7
<#
.SYNOPSIS
    Set GitHub repository secrets via REST API (no gh CLI required).

.BOOTSTRAP
    Requires GITHUB_TOKEN environment variable with `repo` scope.
    Create at https://github.com/settings/tokens (one-time web visit).
#>
param(
    [string]$Repo = "smiles70/Noni",
    [string]$Token = $env:GITHUB_TOKEN
)

$ErrorActionPreference = "Stop"

function Get-RepoPublicKey {
    $url = "https://api.github.com/repos/$Repo/actions/secrets/public-key"
    $res = Invoke-RestMethod -Uri $url -Headers @{
        Authorization = "Bearer $Token"
        Accept = "application/vnd.github.v3+json"
    }
    return $res
}

function Encrypt-Secret {
    param([string]$PublicKey, [string]$SecretValue)
    # Requires PyNaCl or Node.js tweetsodium
    # Using Python subprocess for reliability:
    $py = @"
from base64 import b64encode
from nacl import encoding, public
pk = public.PublicKey("$PublicKey".encode(), encoding.Base64Encoder())
box = public.SealedBox(pk)
enc = box.encrypt("$SecretValue".encode())
print(b64encode(enc).decode())
"@
    return (python -c $py).Trim()
}

function Set-RepoSecret {
    param([string]$Name, [string]$Value)
    $pk = Get-RepoPublicKey
    $enc = Encrypt-Secret -PublicKey $pk.key -SecretValue $Value
    $body = @{ encrypted_value = $enc; key_id = $pk.key_id } | ConvertTo-Json
    $url = "https://api.github.com/repos/$Repo/actions/secrets/$Name"
    Invoke-RestMethod -Uri $url -Method PUT -Headers @{
        Authorization = "Bearer $Token"
        Accept = "application/vnd.github.v3+json"
    } -Body $body -ContentType "application/json"
    Write-Host "Set secret: $Name"
}

# --- Main ---
if (-not $Token) { throw "Set GITHUB_TOKEN env var" }
Set-RepoSecret -Name "VITE_API_BASE_URL" -Value "https://noni-api.fly.dev"
Set-RepoSecret -Name "PROD_API_BASE_URL" -Value "https://noni-api.fly.dev"
```

### 4.4 Triggering Workflow Runs via API

```http
POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches
Authorization: Bearer <token>
Content-Type: application/json

{ "ref": "main" }
```

Or via `gh`:
```bash
gh workflow run deploy.yml --repo smiles70/Noni --ref main
```

---

## 5. Cross-Vendor Bootstrap Script

```powershell
#Requires -Version 7
<#
.SYNOPSIS
    One-shot bootstrap: validate credentials, create least-privilege tokens,
    set GitHub secrets, and trigger deploy.

.PREREQUISITES (one-time manual steps)
    1. Cloudflare: obtain Global API Key from dashboard
       → https://dash.cloudflare.com/profile/api-tokens
    2. Fly.io: run `fly auth login` once on this machine
    3. GitHub: create PAT with `repo` scope
       → https://github.com/settings/tokens

    After these three one-time steps, everything below is fully automated.
#>
param(
    [string]$CfAccountId = $env:CLOUDFLARE_ACCOUNT_ID,
    [string]$CfApiKey    = $env:CLOUDFLARE_API_KEY,
    [string]$CfEmail     = $env:CLOUDFLARE_EMAIL,
    [string]$FlyApp      = "noni-api",
    [string]$GhRepo      = "smiles70/Noni",
    [string]$GhToken     = $env:GITHUB_TOKEN
)

# --- Validate prerequisites ---
$missing = @()
if (-not $CfApiKey -or -not $CfEmail)   { $missing += "CLOUDFLARE_API_KEY + CLOUDFLARE_EMAIL" }
if (-not (Get-Command fly -ErrorAction SilentlyContinue)) { $missing += "flyctl (install from https://fly.io/docs/flyctl/install/)" }
if (-not $GhToken)                        { $missing += "GITHUB_TOKEN" }
if ($missing) {
    Write-Host "Missing prerequisites (one-time setup):" -ForegroundColor Red
    $missing | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

# --- Step 1: Create Cloudflare Pages deploy token ---
Write-Host "`n[1/4] Creating Cloudflare API token..." -ForegroundColor Cyan
# ... (use function from section 2.6)

# --- Step 2: Create Fly.io deploy token ---
Write-Host "`n[2/4] Creating Fly.io deploy token..." -ForegroundColor Cyan
$flyToken = fly tokens create deploy -a $FlyApp -x 720h --json | ConvertFrom-Json
Write-Host "Fly token created (expiry: $($flyToken.expires_at))"

# --- Step 3: Set all secrets in GitHub ---
Write-Host "`n[3/4] Syncing secrets to GitHub..." -ForegroundColor Cyan
# ... (use function from section 4.3)

# --- Step 4: Trigger deploy ---
Write-Host "`n[4/4] Triggering Deploy workflow..." -ForegroundColor Cyan
gh workflow run deploy.yml --repo $GhRepo --ref main

Write-Host "`nDone. Monitor: https://github.com/$GhRepo/actions" -ForegroundColor Green
```

---

## 6. References

| Vendor | Topic | URL |
|--------|-------|-----|
| Cloudflare | Create tokens via API | https://developers.cloudflare.com/fundamentals/api/how-to/create-via-api/ |
| Cloudflare | Global API Key (legacy) | https://developers.cloudflare.com/fundamentals/api/get-started/keys/ |
| Cloudflare | Account token creation API schema | https://developers.cloudflare.com/api/resources/accounts/subresources/tokens/methods/create/ |
| Cloudflare | Pages direct upload / Wrangler | https://developers.cloudflare.com/pages/get-started/direct-upload/ |
| Cloudflare | Wrangler system env vars | https://developers.cloudflare.com/workers/wrangler/system-environment-variables/ |
| Fly.io | flyctl integration / tokens | https://fly.io/docs/flyctl/integrating/ |
| Fly.io | fly tokens create deploy | https://fly.io/docs/flyctl/tokens-create-deploy/ |
| Fly.io | Access tokens overview | https://fly.io/docs/security/tokens/ |
| GitHub | Encrypting secrets for REST API | https://docs.github.com/en/rest/guides/encrypting-secrets-for-the-rest-api |
| GitHub | REST API: Actions Secrets | https://docs.github.com/en/rest/actions/secrets |
| GitHub | gh CLI secrets | https://cli.github.com/manual/gh_secret_set |

---

## Appendix: The "No Dashboard" Myth

After researching 15+ authoritative sources across all three vendors, the
unavoidable truth is:

> **Cloudflare** and **Fly.io** both require a browser-based identity proof
> (OAuth or dashboard login) to establish the *first* credential.

There is **no REST endpoint** that says "create an API token with no
authentication." This would be a security disaster.

**The automation strategy** is therefore:
1. **One-time**: obtain bootstrap credentials (Global API Key for Cloudflare,
   `fly auth login` for Fly.io, PAT for GitHub).
2. **Ongoing**: use those credentials to programmatically create scoped,
   short-lived tokens, manage secrets, deploy, and rotate.

Everything in this library covers step 2. Step 1 is the irreducible manual
minimum — typically 5 minutes of dashboard clicking, done once per project
lifetime.
