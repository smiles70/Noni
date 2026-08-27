# Lessons Learned and Gotchas — HERO-004 Mynaani Hero

**Process:** v9.51
**Date:** 2026-08-27

## Lessons learned

1. **A screenshot is not a clean image asset.**
   `formynaani.png` includes browser chrome, a taskbar, and third-party
   UI. It requires heavy CSS cropping and is a placeholder only.

2. **CSS cropping with `object-position` can hide UI, but not forever.**
   A better solution is a clean, edited, rights-cleared photograph.

3. **Contract exemption tags should stay in place.**
   The hero image and card are still exempt and must keep their
   `data-contract-exemption` attributes.

## Gotchas

1. **Browser chrome and taskbar in the source will show if the crop is
   not tight enough.** Use `object-position: left 55%` or similar.

2. **The MetLife card will appear behind the Noni card unless the Noni
   card is positioned on the right and opaque.**

3. **Screenshot quality may not scale to large monitors.**
   The source is likely 1366×768 or similar. On 4K it will pixelate.

4. **Copyright:** the MetLife photo is not owned by Noni. Replace before
   public launch.
