# 0013 - Bundle-size budget enforced in CI

## Status

Accepted (Sprint 15).

## Context

The frontend bundle is currently ~63 kB gzipped. Without a CI gate, every dependency added compounds silently. For Noni's audience - older adults often on slow or metered connections - bundle size is a measurable component of the calm-experience promise.

## Decision

- `frontend/scripts/check-bundle-size.mjs` reads every JS chunk in `dist/assets/`, gzips it in-memory, and asserts each chunk is at or under **100 kB gzipped**.
- Wired as `npm run bundle-size`.
- The CI `frontend` job runs `npm run build` then `npm run bundle-size`. A regression fails the build.
- 100 kB threshold gives ~60% headroom over today's 63 kB but flags any single-PR jump of 35 kB or more.
- Per-chunk (not total) so future code-splitting is encouraged.
- Gzipped (not raw) because that is what users transfer.

## Consequences

- Bundle bloat is visible at PR time, the only point at which it is cheap to address.
- Raising the threshold requires a deliberate ADR.
- Script is dependency-free (Node built-ins). No supply-chain surface.
