# HERO-006 Findings — High-Resolution Original `formynaani` Image

**Process:** v9.51
**Date:** 2026-08-27
**Reference:** `/home/hazbyn/Downloads/formynaani.png` (1280×720)
**Scope:** Research only. No code or landing-page changes.

## Executive summary

The high-resolution original of the two-women MetLife landing photo is **not
available on the public web**. It lives behind MetLife's internal Digital Asset
Management (DAM) / Adobe Brand Portal, which requires a MetLife login and
Global Brand Review for hi-res download.

## What I found

### 1. Internal MetLife DAM

- MetLife DAM landing page: `https://dam.metlife.com/`
- Brand Portal (login required):
  `https://metlifeglobal.brand-portal.adobe.com/mediaportal.html/content/dam/mac/metlifeglobal/metlife-assets/marketing/photography`
- The DAM FAQ explicitly states that **hi-res assets require approval** and are
  delivered via share-file link after a Global Brand Review.
- Contact: `DAM@metlife.com`

### 2. Direct source

- Screenshot source: `https://dev.mam.metlife.com/dep/landing`
- The domain `dev.mam.metlife.com` does not resolve publicly.
- No image URL pattern could be discovered from the 1280×720 screenshot.

### 3. Warren Seuradge / SID LEE MetLife campaign gallery

- Case study: `https://www.warrenseuradge.com/work/metlife-cx`
- Extracted 28 low-resolution (750×500) WebP images.
- No exact match for the two women in `formynaani.png`.
- Several filenames reference the "Ageing Parents Living Room" series, e.g.,
  `MT_Ayala_US%26MEX_AgeingParents_LivingRoom_152.jpg`, but the downloaded
  thumbnail was a different scene.

### 4. Live MetLife Legal Plans site

- `https://www.metlifelegal.com/assets/img/hero-couple-latino-reverse.webp`
  (1000×666) — different couple on a couch.
- `https://www.metlifelegal.com/assets/img/metlife.bg2.webp` (1920×647) —
  abstract gradient, not the photo.
- The live site no longer uses the two-women image from the screenshot.

### 5. Public image searches

- Pexels, Unsplash, Pixabay, Freepik, Pikwizard: only free alternatives, not the
  original.
- Reverse search for the original filename `formynaani`: no matches.
- Warren Seuradge, Jo Metson Scott, and Ellie Smith public portfolios: no
  matching high-res frame.

## Conclusion

The original high-resolution photograph is an internal MetLife asset. As a
MetLife officer, you can obtain it by:

1. Logging into `https://metlifeglobal.brand-portal.adobe.com/mediaportal.html`
2. Searching the photography section for the campaign (likely "Navigating Life
   Together" or the MetLife Legal Plans individual landing page).
3. If it is not publicly listed in the portal, email `DAM@metlife.com` with the
   screenshot (`formynaani.png`) and request the original file.
4. For hi-res, submit the layout for Global Brand Review per the DAM FAQ.

## Recommended next step

Send `DAM@metlife.com` the screenshot and request the high-resolution file for
the MetLife Legal Plans `dev.mam.metlife.com/dep/landing` hero. They can provide
it directly; I cannot access the login-protected DAM from here.
