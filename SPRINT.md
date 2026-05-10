# Sprint 15: Bundle-Size Budget (CLOSED)

Tag: `sprint-15-bundle-budget-v1`. Adds a CI gate so frontend bundle bloat fails the build.

## Phases

- 15.1 `frontend/scripts/check-bundle-size.mjs` (dependency-free, gzip in-memory, per-chunk)
- 15.2 `npm run bundle-size` script
- 15.3 CI: build then bundle-size, fails on regression
- 15.4 ADR 0013

## Threshold

100 kB gzipped per chunk. Current bundle is ~62 kB.
