# Verification memo — PS-BID17-025 (mobile touch target on /)
Reproduced on prod at iPhoneSE viewport: failing element identified as
the LandingFooter "Help" link (42.86px wide). Root cause: LINK style
set minHeight but no minWidth. Fix: minWidth+justifyContent via
MIN_TOUCH_TARGET.mobile token. Verified 140/140 on staging, 36/36 prod.
