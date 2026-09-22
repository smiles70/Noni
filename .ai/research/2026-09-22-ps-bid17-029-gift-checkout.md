# Verification memo — PS-BID17-029 (/gift restyle)
Codebase checks: GiftCheckoutPage (125 lines) uses AccountStyles imports;
submit path = startGuestCheckout() → res.checkout_url → location.assign
(L44-45); email regex validation before POST; ChatWidget mounted at L120
(inside card div) AND L122 (outside main div) — duplicate mount, script
dedupes by id "retell-widget" (ChatWidget.tsx L40). Treatment = aligned
paper/card/gold per /c/:slug precedent; no hero band (Jev 0.59 hedged —
conservative). Deviation from ≥20-source protocol: defect restyle.
