---
description: Provision or re-provision the Clerk dev instance (auth, link, snapshot config). Used when onboarding a new developer or recreating the local Clerk app.
---

# Set up Clerk for local development

This workflow takes a fresh dev machine to "Noni runs against our Clerk
dev instance" with the smallest number of clicks possible. The only
non-scriptable step is the one-time browser-based `clerk auth login`
(which writes credentials to `~/.config/clerk-cli/`). Everything else
is fully automated.

Source of truth for the instance configuration lives at
`.clerk/config.json` (committed to git). After running this workflow,
`clerk doctor` should pass all checks and `clerk config pull` should
emit a diff-clean copy of that file.

ADR reference: 0024 (Clerk migration).

## Prerequisites

- WSL or Linux/macOS shell. (Native Windows is untested.)
- A GitHub account with push access to this repo (Clerk links instances
  to apps via git remote, so the remote URL must match).

## 1. Install the Clerk CLI

The npm package has had platform-binary issues on WSL (see
github.com/clerk/cli for the upstream tracker). The curl installer is
the reliable path.

// turbo
```bash
curl -fsSL https://clerk.com/install | bash
```

If the installer reports that `~/.local/bin` is not on `PATH`,
persist it and re-source:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"
clerk --version
```

## 2. Authenticate (one-time, per machine)

Opens a browser; complete the Clerk login flow; close the tab when
the CLI confirms success. Credentials persist in
`~/.config/clerk-cli/config.json`.

```bash
clerk auth login
```

## 3. Link this repo to the Noni Clerk app

The CLI uses your `git remote get-url origin` to find the right app.
Confirm the `noni` app in the interactive picker (or use
`--input-json` for non-interactive runs).

```bash
clerk link
```

Expected: `Linked to noni in <repo path>`.

## 4. Verify the link and the live config matches what's in git

// turbo
```bash
clerk doctor
```

All checks should pass. Two non-fatal warnings are acceptable:
- "production not configured" — expected; we don't have prod yet.
- ".env is missing CLERK_*" — only relevant for session 3 (backend
  JWT verification). Frontend uses `VITE_CLERK_PUBLISHABLE_KEY` which
  is set manually below.

Diff the live config against the committed snapshot. A non-empty diff
means someone changed the dev instance via the dashboard and didn't
sync it back — re-pull the snapshot and commit if intentional, or
revert via `clerk config push .clerk/config.json` if not.

```bash
diff <(clerk config pull) .clerk/config.json || echo "drift detected"
```

## 5. Wire the publishable key into the frontend

Until `clerk env pull` can emit `VITE_`-prefixed names (open feature
request upstream), we set the publishable key manually.

Get the key from the Clerk dashboard (or from `clerk api ls` to
discover the right endpoint, then `clerk api instances/<id>/api_keys`).
Then append to `.env`:

```bash
cat >> .env <<EOF

# --- ADR 0024: Clerk migration ---
VITE_AUTH_PROVIDER=clerk
VITE_CLERK_PUBLISHABLE_KEY=pk_test_REPLACE_ME
EOF
```

Rebuild the frontend so Vite bakes in the new env:

```bash
docker compose build frontend && docker compose up -d
```

## 6. Smoke test

Open `http://localhost:8080` in incognito, click Log in, complete
Clerk sign-in, then in DevTools console look for:

```
[ClerkAuthBridge] Clerk session token (length=...)
```

If you see that line, the frontend is correctly wired to Clerk and
session 2 of the migration is verified end-to-end on this machine.

## What this workflow does NOT do (yet)

- **Backend JWT verification.** That's session 3. Will add a step here
  to pull `CLERK_SECRET_KEY` and append it to `.env` for the backend.
- **Production instance.** Session 4. Will introduce
  `clerk apps create --name noni-prod` and a parallel `.clerk/config.prod.json`.
- **Push config changes back to Clerk.** When we change
  `.clerk/config.json` (e.g. to set an `after_sign_in` redirect),
  apply it with `clerk config push .clerk/config.json`. Not wired
  into this workflow yet because dev config rarely changes.
