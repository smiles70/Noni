# Lessons Learned and Gotchas — HERO-003 Full-Page Hero Image

**Process:** v9.51
**Date:** 2026-08-27

## Lessons learned

1. **Full-page images behave differently from contained cards.**
   `object-fit: cover` alone does not guarantee the subject appears in a
   usable part of the frame. `object-position` is required to anchor the
   subject to the side opposite the action card.

2. **Dark overlays can flatten a full-page photograph.**
   A heavy overlay makes a full-page image look muddy. When the text lives
   inside a solid card, the overlay can be lighter or removed.

3. **The image file is the long pole, not the layout.**
   Once the layout supports `object-position` and a floating card, the
   remaining work is sourcing or licensing a correctly composed photograph.

## Gotchas

1. **The placeholder `nonisplash.jpg` may not have the subject on the left.**
   `object-position: left center` only works if the subject is already
   positioned toward that side in the source image. A replacement image
   with a centered or right-side subject may need a different value.

2. **A right-side card can still obscure the subject if the image is too narrow.**
   Use a wide image (≥ 1920 px) and a `maxWidth` on the card that does not
   exceed the safe zone.

3. **Mobile stacking needs manual testing.**
   A fixed right card with `position: absolute` can overflow on a short
   mobile viewport. Keep the card short and allow vertical scrolling.

4. **Image licensing and third-party references remain a concern.**
   Do not copy the MetLife photograph. Use a rights-cleared image or
   generate an original one.

5. **Contract exemption tags must be preserved.**
   Any new full-page image or layout elements must keep
   `data-contract-exemption="landing.hero"` so the exemption remains auditable.
