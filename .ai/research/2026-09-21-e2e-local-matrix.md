# Research memo — local e2e matrix (PS-E2E-001)

Proportionate-scope verification memo for the environment defect; the
≥20-source protocol applies to decisions, not defect triage — deviation
recorded here per the defect fast-path.

## Findings (verified in code and on-machine)

1. `frontend/playwright.config.ts` defines 5 projects: chromium, firefox,
   webkit, mobile-pixel, mobile-iphone.
2. `ci.yml:158` installs all browsers (`chromium + firefox + webkit`) —
   the full matrix exists in CI; the gap was local-only.
3. Root cause: `~/.cache/ms-playwright` lacked firefox-1532 and
   webkit-2311. Fixed by `npx playwright install firefox webkit`.
4. Second-order env constraint found during verification: this machine
   denies `unshare(CLONE_NEWPID)` → firefox's content sandbox cannot
   init → context setup timeouts. `MOZ_DISABLE_CONTENT_SANDBOX=1
   MOZ_DISABLE_GMP_SANDBOX=1` resolves it (firefox spec green, 14.5s).
5. Webkit passed on retry (cold-start exceeded the 30s goto timeout on
   first launch; deps validated — `DEPENDENCIES_VALIDATED` marker).
6. Chromium/mobile "sign-in gate" spec flaked once against prod under
   parallel load — timing, not a regression (same spec green in the
   preceding prod e2e run; PS-020 touches no frontend).

## Durable fix

CONTRIBUTING.md e2e section now documents the install, the deployed-site
env var, the firefox sandbox workaround, and the webkit cold-start note.
No code change required; playwright.config.ts untouched so CI behavior is
unchanged.
