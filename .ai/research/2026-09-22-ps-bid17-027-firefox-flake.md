# Verification memo — PS-BID17-027 (firefox help-card flake)
Failed once on prod matrix (5s expect timeout on swapped-view heading),
green on retry 6.4s — flake confirmed, not defect. Fix:
waitForLoadState("networkidle") before the Help click — assertion
unchanged. Green in CI e2e (10m25s) + prod firefox run.
