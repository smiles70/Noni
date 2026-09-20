# PS-BID17-019 — Logo size parity check: mock vs staging (measurement)

**Status:** RESOLVED — pixel-identical confirmed; delta was stale browser cache
**Source:** owner request 2026-09-20

## Measurement findings

- Mock: `AGENCY_BIDS/bid-17-caregiver.html` → `.logo img{height:56px}`
- Staging: `CaregiverPage.tsx` → `<img height={56}>`, same file
- Asset: `mynaani-icon-linework-dark.svg` — **md5-identical** in both
  (`ce0ccdaf19a993e6566e3bad124d0af1`)
- Conclusion: spec-identical. Perceived delta = screenshot scaling,
  not a rendering difference.

## If the intent is a BIGGER logo on staging

| Option | Change | Trade-off |
|---|---|---|
| A. Bump height | `height:56→64/72` one line | nav grows; vector scales cleanly, zero cost |
| B. Stacked wordmark | swap to `mynaani-logo-stacked-color-dark.svg` (in AGENCY_BIDS) | bigger visual presence incl. text; different look |
| C. Crop viewBox | tighten 431×286 canvas | no code change; risk of clipping if bounds mis-measured |

## Steps to deploy whichever chosen

1. Update `CaregiverPage.tsx` + `ForCommunitiesPage.tsx` (and Footer
   dark variant if footer logo changes too — footer is 44px in mock).
2. Same-commit test pin if tests assert the logo img height.
3. Push → staging deploy → visual confirm.

## Needs owner

- Which target: A (bigger mark, same art), B (stacked wordmark), or
  confirm 56px is correct and no change needed.


## Pixel-level verification (2026-09-20)

Playwright renders + in-browser RGBA diff (.ai/audit/visual-diff/):

- mock nav logo: 84.4×56px, `mynaani-icon-linework-dark.svg`
- staging nav logo: 84.4×56px, same file (md5 identical)
- element-level diff: **100% identical — same 4,500 ink pixels**

Root cause of the perceived difference: owner's Firefox cached the
pre-redraw ICON-001 medallion/stacked render under the same filename
(file mtime Sep 19 14:33; renders today). Hard-refresh (Ctrl+Shift+R)
on the mock tab resolves. Confirms LOGO-ICON-003 cache-stale failure
mode; filename versioning already shipped defeats *deployed* cache but
not a file:// page's stale in-memory render.
