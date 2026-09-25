# Research: pixel-accurate visual-diff tooling (PS-019)

**Date:** 2026-09-20 · **Question:** which tooling accurately reads rendered
screenshots and diffs them pixel-by-pixel (color + size)?

## Decision matrix

| Tool | Engine | Speed (1440×900) | Fit |
|---|---|---|---|
| **Playwright `toHaveScreenshot`** | pixelmatch (YIQ perceptual, AA-aware) | ~28ms | SELECTED — already in e2e stack, zero new deps |
| odiff (dmtrKovalenko/odiff) | native Rust | ~3ms (8× faster) | best for bulk full-page diffs; new dep |
| reg-cli (reg-viz) | pixelmatch + HTML report | ~28ms | good human-review UI; new dep |
| ImageMagick compare | RMSE | ~8900ms | slow, no AA-awareness |
| Vision LLM (Claude/Gemini) | semantic | — | complement: judges *what* changed after pixel-diff flags *that* it changed |

## Key references

- mapbox/pixelmatch — de-facto standard, YIQ NTSC color distance
  (Kotsarenko & Ramos 2010), AA detector (Vyšniauskas 2009), ~150 LOC,
  no deps — same engine inside Playwright, jest-image-snapshot,
  BackstopJS.
- playwright.dev/docs/test-snapshots — `threshold` is per-pixel YIQ
  tolerance (default 0.2); `maxDiffPixels`/`maxDiffPixelRatio` are the
  budgets. Commonly misread (Playwright issue #10219).
- dmtrKovalenko/odiff — 8× pixelmatch; used by Argos, Lost Pixel.
- reg-viz/reg-cli — Wasm rewrite, reg-suit compatible.

## Implemented

`.ai/audit/visual-diff/compare.js` — renders mock + staging at identical
viewport, crops nav/footer regions, RGBA diffs in-browser, emits
captures + report.json.

## First-run results (2026-09-20)

- Logo element: **84.4×56 both, 100% identical pixels** — the staged
  logo IS the mock logo; user-facing delta was a stale browser cache
  (ICON-001 medallion cached under the versioned filename).
- nav band: 1366×84 both, ~5.5–6.5% diff (AA/text rendering).
- footer: mock 1366×96 strip vs staging 1366×419 full site footer —
  expected divergence (mock footer was placeholder; staging footer is
  the contract footer). Not a defect.
