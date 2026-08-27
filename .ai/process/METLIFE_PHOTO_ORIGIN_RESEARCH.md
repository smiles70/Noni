# Original-Source Research — MetLife / Mynaani Landing Hero Photo

**Process:** v9.51
**Date:** 2026-08-27
**Input image:** `/home/hazbyn/Downloads/formynaani.png` (1280×720 PNG, screenshot)
**Research goal:** Identify the original, un-watermarked, high-resolution source
of the photograph used in the MetLife landing page.

## What the image contains

- Two women: one older adult with gray hair in a cream/white crochet cardigan,
  one younger woman with dark hair in a green/teal cardigan.
- They are seated close together at what appears to be a kitchen or dining table,
  laughing.
- The image is a screenshot of `https://dev.mam.metlife.com/dep/landing`.

## Search methodology

1. Web search for `dev.mam.metlife.com/dep/landing` and the image description.
2. Web search for MetLife Legal Plans landing-page hero photo.
3. Web search for stock photos matching the description.
4. Web search for the photographers credited on the Warren Seuradge case study.
5. Review of `formynaani.png` EXIF data.

## Findings

### 1. The image is from a custom MetLife brand campaign

The most authoritative source is the Warren Seuradge case study page
`https://www.warrenseuradge.com/work/metlife-cx`:

> "After breaking up with Snoopy and the Peanuts gang, MetLife asked us to create a
> range of human-centered photography to support its 'Navigating Life Together'
> brand platform around the world."
>
> "Working with such renowned photographers as **Jo Metson Scott** and **Ellie Smith**,
> we brought to life little slivers of life across key markets... through the power
> of reportage-style photography."
>
> "We produced over **650 photos** for a range of products/services for global and
> local market use-cases."

This confirms the image is **commissioned, not a public stock photo**. It belongs
to the MetLife photo library created for the "Navigating Life Together" platform.

### 2. Photographers identified

- **Jo Metson Scott** — British portrait / documentary photographer
  (`https://www.jometsonscott.com/`)
- **Ellie Smith** — British photographer with MetLife in her client list
  (`https://www.linkedin.com/in/ellie-smith-photographer`)

Neither photographer’s public portfolio contains a downloadable copy of this
specific image. Jo Metson Scott’s site is a portfolio of other editorial work;
Ellie Smith’s public pages do not show this frame.

### 3. No public stock match found

Searches across:

- Getty Images
- Depositphotos / PeopleImages
- iakovenko123 portfolio
- Unsplash / Pikwizard / Megapixl
- General web

found *similar* concepts (older woman + younger woman in kitchen/living room),
but **not the same two people, clothing, or composition**. The distinctive
crochet cardigan, the laughing pose, and the dark-haired younger woman did not
appear in any public stock index.

### 4. EXIF analysis of `formynaani.png`

```
size (1280, 720)
info {'gamma': 0.45455, ..., 'dpi': (96.012, 96.012)}
mode RGBA
```

- The file is an **RGBA screenshot**, not a camera original.
- DPI is 96, typical of screen captures.
- No camera, copyright, or author metadata.
- No original filename or source URL embedded.

### 5. Direct source URLs are not reachable

- `https://dev.mam.metlife.com/dep/landing` — could not fetch (internal/dev).
- `https://www.metlifelegal.com/` — returned content but not the hero photo.
- `https://www.metlife.com/insurance/legal-plans/` — content did not expose the
  original image asset.

## Conclusion

The original photograph is **not publicly available**. It is part of the MetLife
"Navigating Life Together" commissioned library, photographed by Jo Metson Scott
and/or Ellie Smith for Warren Seuradge / SID LEE. It is an enterprise-owned
asset, not a stock image.

## Implications for Mynaani

- **Cannot use this image in production without a license.**
- The screenshot in `Downloads/formynaani.png` is a copyrighted third-party work.
- For a live Mynaani landing page, a rights-cleared or original replacement is
  required.

## Recommended next steps

1. **Option A — License the original from MetLife / the photographers.**
   Contact Warren Seuradge, Jo Metson Scott, or Ellie Smith to license the
   specific frame. This is likely expensive and slow.

2. **Option B — Commission a similar photo.**
   Hire a photographer to create an original older-adult + younger-adult image
   in a home setting.

3. **Option C — Use a close-enough stock photo with full rights.**
   Sources like Unsplash, Pexels, or Getty have similar concepts; purchase a
   high-resolution, royalty-free license.

4. **Option D — Use `nonisplash.jpg` (current live placeholder).**
   The existing Mynaani-owned image is legally safe but visually less aligned with
   the MetLife reference.
