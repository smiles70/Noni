# Verification memo — PS-BID17-030 (/gift-redeem restyle)
Codebase checks: GiftRedeemPage (274 lines, AccountStyles); routing via
props — onClaimed→goPaidCurriculum + onBack→/paywall + onHelp→/help wired
in App.tsx L463-467; RequireAuth wraps route L462. Guard contract:
post-redemption must hit paid track — pinned. Aligned treatment, no
widget (recipient mid-transition). Protocol deviation documented.
