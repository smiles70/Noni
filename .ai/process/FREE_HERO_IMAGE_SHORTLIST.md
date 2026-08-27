# Free Hero Image Shortlist — MetLife-Style Landing Photo

**Process:** v9.51
**Date:** 2026-08-27
**Goal:** Find a rights-free, high-resolution image matching the MetLife
reference: an older woman and a younger adult woman, warm tones, joyful,
home-like setting, full-bleed capable.

## Reference

- `formynaani.png` (1280×720 screenshot of MetLife landing page)
- Key visual: older adult + younger adult, warm golden/cream/green palette,
  natural light, shallow depth, subject on left, open right side for card.

## Sites searched

1. **Pexels** — direct `images.pexels.com` downloads.
2. **Unsplash** — free Unsplash License results.
3. **Pixabay** — Pixabay Content License results.
4. **Freepik** — free and premium results.
5. **Pikwizard** — free stock results (site blocked by Cloudflare during fetch).

## Shortlist

| Rank | Site | ID / URL | Description | Size | License | Notes |
|---|---|---|---|---|---|---|
| 1 | Pexels | `3768131` | Joyful adult daughter greeting senior mother in sunny garden. Older woman in cream cardigan, adult daughter in brown, warm golden bokeh. | 1620×1080 (fetched) | Pexels License | **Selected and deployed.** Strongest match for warm palette and two-women subject. |
| 2 | Pexels | `6148959` | Younger and senior women holding hands and laughing in autumn garden. | 1125×750 | Pexels License | Bright, red/white, open background. |
| 3 | Pexels | `7232031` | Elderly woman in blue turtleneck beside a younger woman indoors. | 1125×750 | Pexels License | Calm, indoor, muted but less joyful. |
| 4 | Unsplash | `ycGV6R9HzU8` | Close-up senior mother and adult daughter hugging and laughing. | varies | Unsplash+ (premium) | Premium — not free. |
| 5 | Pikwizard | `b0e476ae2922ed3a5ce12ce69377f7e6` | Senior woman and adult daughter laughing in modern kitchen. | unknown | Royalty-free | Site blocked by Cloudflare; could not fetch. |
| 6 | Pixabay | search results | Mostly single-grandmother or young-child photos. | — | — | No strong two-adult match. |
| 7 | Freepik | search results | Mostly children/grandchildren; few free adult-daughter matches. | — | — | No clear top free match. |

## Selection

**Pexels 3768131** was chosen because:
- Two women: older adult + adult daughter.
- Warm, natural, golden/cream/brown color palette closest to the MetLife reference.
- Shallow depth of field gives an open right side for the Noni action card.
- 1620×1080 resolution is sufficient for full-bleed hero without visible pixelation.
- Pexels License allows free use with no attribution required.

## Files

- `frontend/public/hero-pexels.jpg` — deployed asset.
- `frontend/src/components/LandingPage.tsx` — updated `src` and `object-position`.

## License note

Pexels images are free to use without attribution under the Pexels License,
but attribution is appreciated. For a production site, an `ATTRIBUTION.md`
line can be added: "Photo by Pexels on Pexels."
