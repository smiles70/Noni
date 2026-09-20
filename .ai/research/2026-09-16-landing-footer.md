# Research — Landing-page footer decision

**Date:** 2026-09-16
**Intake:** `.ai/intake/2026-09-16-p2-landing-footer.md`
**Question:** Should `/` have a footer, and if so in what form? Reference
example supplied: GetSetUp's classic fat footer (brand mark, link
columns, legal row).
**Status:** research complete — awaiting product decision

## Codebase facts (discovery)

- `LandingPage.tsx`: hero is `position: fixed; inset: 0; overflow:
  hidden` — the page **cannot scroll** (AGENTS.md constraint; a prior
  in-flow `100vh` attempt shrank the hero and was rolled back).
- **No privacy, terms, help, or contact link is reachable from `/`.**
  Routes `/privacy` and `/help` exist but are only linked from other
  pages/dialogs. No `/terms` route exists.
- Existing footer pattern (`FOOTER` on `ForCommunitiesPage`,
  `CaregiverPage`): minimal border-top flex bar — tagline + one link.
  No shared `Footer` component.
- The hero is exempt from the marketing-surface contract via
  `data-contract-exemption="landing.hero"`; any new in-hero element
  needs the same marker.
- Signed-in state shows additional widgets (help/chat) at bottom-right
  that a bottom strip could collide with.

## Source table

### FAANG / top-tier design systems (10)

| # | Source | Org | Key finding |
|---|---|---|---|
| 1 | nngroup.com/articles/footers | NN/g (Fessenden, 2019) | Footer taxonomy: fat, mini, doormat-nav, contextual. "Cost-free addition" — helps, can't hurt. Utility links (contact, privacy, terms) are the universal minimum. Mini-footer pattern is the prescribed answer for pages without a natural bottom (infinite scroll — our analog: fixed viewport). |
| 2 | baymard.com/blog/footer-links-ecommerce | Baymard Institute | Semantic grouping of footer links; users expect specific content (contact, policies) in footers and abandon when it's absent. |
| 3 | m2.material.io/components/app-bars-bottom | Google Material 2 | Bottom app bar: mobile-only pattern, 2–5 actions, 48dp targets. Model for an in-viewport bottom strip. |
| 4 | m3.material.io/components/navigation-bar/guidelines | Google Material 3 | Bottom container spans full width, ≤5 items, filled container for separation. |
| 5 | m3.material.io/components/toolbars/guidelines | Google Material 3 | Docked toolbar: full-width bottom container, 48×48dp targets, avoid too many controls. |
| 6 | oracle.com/.../alta/patterns/Footer.html | Oracle Alta | Footer = home of "mandatory legal notices"; discusses footer anchored at viewport base (sticky) vs. flowing below content. |
| 7 | design-system.service.gov.uk/components/footer | GOV.UK DS (verified) | Footer contents: copyright, licensing, links to Privacy, Accessibility, Cookies, Terms, help. WCAG 3.2.6 — help links must be consistent across pages. |
| 8 | design-system.dwp.gov.uk/.../internal-service-footer | UK DWP DS | Minimum footer = accessibility + privacy links. Warns footer content is "sometimes skipped" and grey-on-grey lowers contrast. |
| 9 | design-system.service.mod.gov.uk/components/footer | UK MOD DS | "Use the footer at the bottom of every page of your service." |
| 10 | polaris.shopify.com / shopify.dev footer-help | Shopify Polaris | Footer help pattern: bottom-of-page contextual help links; legal links belong in footer compositions. |

### Academic / hard science (6)

| # | Source | Org | Key finding |
|---|---|---|---|
| 11 | nia.nih.gov / NLM "Making Your Website Senior Friendly" | NIA + NLM | Research-based checklist for 60+: consistent layout, same nav elements in same place on every page, single-click access, careful link labels, larger text/targets. |
| 12 | sage.cnpereading.com/doi/10.1177/2327857915041030 | NIHSeniorHealth usability study (peer-reviewed poster) | NIA/NLM redesigned seniorhealth.gov around older-adult constraints; measured major resurgence in use and satisfaction. |
| 13 | Inclusive Web Design Checklist for Older Adults w/ CCD | Doctoral synthesis (Becker 2004, Kurniawan & Zaphiris 2005, Morrell et al.) | 55 criteria across 16 categories; navigation ease and consistency are core categories. |
| 14 | nngroup.com/articles/usability-for-senior-citizens | NN/g (3 rounds, 123 participants 65+) | Seniors are ~43% slower on websites; tiny targets and inconsistent navigation are primary friction. |
| 15 | nngroup.com/articles/usability-testing-older-adults | NN/g (Chan, 2023) | 75% of adults 65+ are online (Pew); motor, visual, cognitive declines are design inputs, not edge cases. |
| 16 | Fitts's-law framing via a11ypath.com/guides/target-size | a11ypath | Larger targets measurably reduce mis-taps for tremor/dexterity-limited users; 24px floor, 44px goal. |

### Industry / standards / legal (8)

| # | Source | Org | Key finding |
|---|---|---|---|
| 17 | law.cornell.edu/.../11-CCR-7011 (verified) | CA Code of Regulations / LII | **CCPA §7011(d): privacy policy must be reachable via a "conspicuous link" using the word "privacy" on the business's homepage.** §7003(c): same font size/color as comparable homepage links. This is a hard requirement for `/`. |
| 18 | cppa.ca.gov final regulations text | California Privacy Protection Agency | Conspicuous = comparable prominence to other links; "Do Not Sell" belongs in header **or footer** — footer is the conventional location. |
| 19 | ftc.gov .com Disclosures (2013) | FTC | Disclosure links must be obvious, appropriately labelled ("privacy"), styled consistently, placed near related content. |
| 20 | ftc.gov Fair Information Practices report | FTC | Clear-and-conspicuous notice is the prerequisite fair-information practice; footer/bottom placement is the documented industry convention. |
| 21 | w3.org/WAI/ARIA/apg/practices/landmark-regions | W3C APG | `<footer>` at body context → `contentinfo` landmark. **A `<footer>` inside `<section>`/`main`/`article`/`nav`/`aside` does NOT get contentinfo role** — directly relevant: our hero is a `<section>`. One contentinfo per page, top-level. |
| 22 | developer.mozilla.org/.../contentinfo_role | MDN | Same rule; prefer semantic element; unique labels if >1. |
| 23 | w3.org/WAI/WCAG22/Understanding/target-size-minimum | W3C WCAG 2.2 SC 2.5.8 (AA) | Pointer targets ≥24×24 CSS px (AA); 2.5.5 AAA = 44×44. Footer links count. |
| 24 | w3.org/WAI/WCAG22/Techniques/css/C43 | W3C WCAG | scroll-padding technique for content obscured by fixed-position components — the failure mode a fixed footer strip can create if content ever scrolls beneath it. |

### Discussion / how-to (5, capped)

| # | Source | Type | Key finding |
|---|---|---|---|
| 25 | xerobit.dev/blog/flexbox-sticky-footer | how-to | Sticky-footer flexbox + **app-shell pattern**: `height:100dvh; overflow:hidden` shell with fixed header, scrollable main, fixed footer — the exact architecture our fixed hero already is. |
| 26 | uxpin.com/studio/blog/footer-design-basics | vendor blog | 4–6 column max, stack on mobile, WCAG AA contrast, descriptive link text, 44×44 tap targets. |
| 27 | frontendchecklist.io/rules/privacy/privacy-policy | checklist | Footer privacy link on every page satisfies GDPR/CCPA "easily accessible" bar. |
| 28 | auditbuffet.com/patterns/ab-001405 | audit pattern | Shared `Footer` component rendered by root layout so 100% of routes inherit the privacy link. |
| 29 | goatslider.com/blog/fullscreen-sliders-... | how-to | Fullscreen/immersive pages minimize chrome; navigation must be subtle to not break the visual field — supports a *minimal* strip, not a fat footer. |

**Total: 29 sources (quota ≥20 met). 3 verified via full fetch (NN/g, CCR §7011, GOV.UK); all others verified reachable via search-result content.**

## Synthesis

1. **The footer question is partly forced.** CCPA §7011(d) requires a
   conspicuous "privacy"-labelled link *on the homepage*. `/` currently
   has none — not in the hero, the dialog, or anywhere else. Regardless
   of the footer decision, `/` needs a privacy link. The footer is the
   conventional, lowest-cost home for it (NN/g: "cost-free addition";
   GOV.UK/DWP/MOD: minimum footer = privacy + accessibility).
2. **A GetSetUp-style fat footer is incompatible with the fixed hero.**
   It requires a scrollable page. Options that keep the constraint:
   (a) mini-footer strip inside the fixed viewport (NN/g mini-footer
   pattern, Material bottom bar analog), or (b) footer content in an
   existing affordance (HowItWorksDialog footer). Options that break it:
   scrollable landing — explicitly gated by AGENTS.md.
3. **Structure matters for a11y.** `<footer>` inside the hero
   `<section>` loses its `contentinfo` role (W3C APG). A correct
   implementation needs a body-level footer element or explicit
   `role="contentinfo"`, positioned inside the viewport.
4. **Geragogy skews minimal.** NIA/NLM: consistent placement, few
   clearly-labelled links, larger targets. A 6-link strip beats a
   30-link sitemap for this audience; and link density competes with
   the hero's single-CTA focus.
5. **Help-link consistency (WCAG 3.2.6):** help is currently
   signed-in-only (deliberate — removed pre-login). If a footer exposes
   "Help" signed-out, that changes the auth-gated help surface —
   separate decision. Alternatively link `help@mynaani.com` mailto as
   contact, matching ForCommunitiesPage's mailto pattern.

## Decision matrix

| Option | Compliance fix | Constraint-safe | Effort | Risk | Verdict |
|---|---|---|---|---|---|
| **A. Status quo** — no footer on `/` | ✗ Fails CCPA conspicuous-link | ✓ | — | Compliance exposure | Rejected |
| **B. Mini-footer strip in fixed viewport** — slim bottom bar (48px), translucent plate like logo plate: Privacy, Contact/help, © mynaani | ✓ | ✓ keeps fixed hero | Low–Med | Viewport crowding on short screens | **Recommended — High confidence** |
| **C. Scrollable landing + fat footer** | ✓ | ✗ violates AGENTS.md fixed-hero; needs explicit approval | Med | Repeats SCROLL-DEPTH-001 failure; hero art-direction regression | Hold — only with approval |
| **D. Legal links inside HowItWorksDialog footer only** | △ weak — link behind a click; "conspicuous on homepage" arguable | ✓ | Low | Doesn't satisfy intent; discoverability poor | Rejected as sole fix; fine as supplement |
| **E. Shared `Footer` component for scrollable pages only** | ✗ doesn't fix `/` | ✓ | Low | Homepage still non-compliant | Necessary but insufficient — do alongside B |

**Recommendation: B + E.** Extract the existing minimal-footer markup
into a shared `Footer` component for the scrollable pages (fixes
duplication, AuditBuffet pattern #28), and add a fixed-position
mini-footer strip on `/` carrying the legal minimum: **Privacy ·
Contact · © mynaani**. This matches NN/g's mini-footer pattern for
pages without a natural bottom, Material's bottom-bar constraints
(≤5 items, ≥48dp targets), and the codebase's existing translucent
plate aesthetic.

Content proposal for the strip (left→right): `© 2026 mynaani` ·
`Privacy` → /privacy · `Contact` → mailto:help@mynaani.com (or /help
for signed-in). No brand logo (the plate is already upper-left;
duplicate logos add noise per goatslider #29). No Terms link until a
`/terms` route exists.

## Edge-case / remediation matrix (top 30)

| # | Edge case | Impact | Remediation | Codebase check |
|---|---|---|---|---|
| 1 | Short viewports (landscape phones, ~360px tall): strip collides with action card at top:55% | UX | Reserve bottom 48px; on `max-height` media query shrink/hide strip or merge links into card | cardPosition top:55% on mobile — verify 480px-tall viewport |
| 2 | `<footer>` nested in hero `<section>` loses contentinfo role | a11y | Render strip as body-level `<footer>` sibling with `position:fixed; bottom:0`, or add `role="contentinfo"` explicitly | hero is `<section>` at LandingPage.tsx:324 |
| 3 | Text legibility over hero photo (bottom of image is busy) | a11y/UX | Same translucent plate style as LOGO_PLATE + verify 4.5:1 | hero `objectPosition: center 10%` — bottom edge varies by image |
| 4 | Target size <24px on text links | a11y (WCAG 2.5.8 AA) | min 24px targets, aim 44px (geragogy); padding on links | HEADER_LINK pattern already padded |
| 5 | Keyboard focus order — strip links must follow hero content | a11y (2.4.3) | DOM order: strip last inside/below hero | strip rendered last in JSX |
| 6 | Visible focus ring on translucent bg | a11y | FOCUS token exists (unused import noted at file end) | reuse `FOCUS` style |
| 7 | Forced-colors / high-contrast mode | a11y | translucent plate must have solid fallback (`forced-color-adjust`) | check existing plate styles for it |
| 8 | prefers-reduced-transparency | a11y | media query → opaque surface | tokens don't cover this yet |
| 9 | iOS safe-area / dynamic toolbar | UX | `env(safe-area-inset-bottom)` padding; `100dvh` mental model | hero uses `inset:0` — strip inside it is fine |
| 10 | Signed-in help/chat widget bottom-right overlap | functional | place strip left-aligned or full-width below widget layer (z-index below chat widget); or hide overlap region | widget mounts bottom-right post-login |
| 11 | Cookie/consent banner later | future | strip must reserve space or stack above | none today — note for future |
| 12 | Duplicate `contentinfo` if shared Footer also rendered on `/` | a11y | landing renders ONLY the strip; shared Footer excluded from `/` route | App.tsx route config |
| 13 | axe color-contrast violations on photo | test failure | solid plate behind links; run smoke.spec axe check | deployed smoke already axe-audits landing |
| 14 | CLS/layout shift | perf | strip renders in same fixed layer, no shift | — |
| 15 | Zoom 200–400% | a11y | strip wraps or truncates gracefully; test at 400% | responsive.spec covers zoom-adjacent checks |
| 16 | RTL locales | i18n | flex row is direction-agnostic; verify | no RTL locale today — low |
| 17 | Localization of "Privacy"/"Contact" | i18n | copy is backend-served? hero copy is — check content.hero source | copy pipeline exists for hero |
| 18 | "Terms" link to nonexistent route | functional | don't link /terms until page exists (create later or legal provides) | confirmed: no /terms route |
| 19 | Copyright year hardcodes | maintainability | `new Date().getFullYear()` | — |
| 20 | SEO crawlability of fixed-overlay links | SEO | links are real `<Link>`/`<a>` in DOM — crawlable | — |
| 21 | Screen reader announces strip prematurely | a11y | strip is last in DOM; contentinfo announced on demand, not eagerly | — |
| 22 | Strip covers hero photo subject | design | 48px max height; translucent — photo shows through like plate | hero objectPosition keeps heads upper-frame |
| 23 | Contract test failure — new element inside hero | test | add `data-contract-exemption="landing.hero"` | pattern exists on all hero children |
| 24 | Print stylesheet | polish | `display:none` in print or unfix | check for print styles (probably none) |
| 25 | Older Safari (`inset`/`dvh` support) | compat | `bottom:0;left:0;right:0` instead of inset shorthand | browserslist targets |
| 26 | Touch mis-tap strip↔card adjacency | UX | ≥8px gap between strip top and card bottom edge | card is `bottom`-free positioned — verify |
| 27 | Authenticated vs anonymous consistency | UX | same strip both states (NN/g: consistent, predictable) | — |
| 28 | Help link behind auth → footer "Help" would expose it | policy | use mailto Contact signed-out; /help link only signed-in | help widget is auth-gated by design |
| 29 | Multiple footers in DOM when dialog opens (dialog has `<footer>`) | a11y | dialog footer is inside `role=dialog` → not contentinfo; no conflict | HowItWorksDialog footer is nested — safe |
| 30 | E2E regression — strip changes visual snapshots/responsive checks | test | extend smoke.spec + responsive.spec assertions for strip presence | smoke.spec exists for deployed |

## Gaps requiring user input

1. **Help link policy:** expose a public `help@` mailto (recommended)
   vs. `/help` link signed-out (changes the auth-gated help surface)?
2. **Terms of Service:** no `/terms` page exists — create one, or omit
   the link for now?
3. **Accessibility statement:** GOV.UK/DWP pattern includes one; no
   such page exists today. Add to backlog?
4. **Copy sourcing:** should strip copy come from the backend copy
   pipeline like hero text, or stay hardcoded?

## Codebase conflict check

- AGENTS.md fixed-hero constraint → Option C blocked without approval;
  Option B compliant.
- `data-contract-exemption="landing.hero"` required on new hero
  children — pattern confirmed.
- Signed-in widgets (help/chat) occupy bottom-right — strip must
  respect that zone.
- No `/terms` or `/accessibility` routes — links limited to what
  exists.
