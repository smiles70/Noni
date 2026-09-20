# PS-BID17-012 — Fifth proof card wraps to second row, uneven grid (defect)

**Status:** fixing | **Severity:** P0 visual defect on staging
**Reported:** owner, staging screenshots 2026-09-20 — "the RCT card goes
to a second row making this section uneven, please remove"

## Problem statement

The evidence section renders 5 proof cards in a 4-column grid — the
"RCT" card wraps alone to row two, leaving an unbalanced band.

## Fix (owner-directed)

Remove the RCT card entirely — 4 cards fill one row evenly.
The Laganà source stays reachable on `/sources` (PS-BID17-004) so the
evidence trail is preserved without the card.

## Alternative considered

Drop to 2×2 grid or shorten to 3 columns — rejected: owner explicitly
directed removal; 4-across matches the bid-17 band rhythm.

## Edge cases

- No unit pin references the RCT card content ("Laganà" appears only in
  the removed list) — verify test suite stays green.
- ForCommunitiesPage proof cards unaffected (different set).
