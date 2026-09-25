import { ReactNode } from "react";
import { useLocation } from "react-router-dom";
import { useViewportContext } from "../context/ViewportContext";
import { MAX_CONTENT_WIDTH, SPACING } from "../styles/responsiveTokens";

interface ContainerProps {
  children: ReactNode;
}

// ADR-0030/0034: bid-17 marketing surfaces render full-bleed color bands
// (nav/hero/CTA edge-to-edge); the learner-track measure cap does not
// apply to them. List is explicit so new annex surfaces opt in
// deliberately rather than accidentally. See
// .ai/intake/2026-09-20-p0-bid17-full-bleed-defect.md
const FULL_BLEED_PATHS = new Set(["/caregiver", "/for-communities"]);

export function ResponsiveContainer({ children }: ContainerProps) {
  const { breakpoint } = useViewportContext();
  const { pathname } = useLocation();
  const fullBleed = FULL_BLEED_PATHS.has(pathname);

  return (
    <div
      style={{
        width: "100%",
        maxWidth: fullBleed ? "100%" : MAX_CONTENT_WIDTH[breakpoint],
        margin: "0 auto",
        padding: fullBleed ? 0 : SPACING[breakpoint].lg,
        boxSizing: "border-box",
        minHeight: "100vh",
        overflowX: "hidden",
      }}
    >
      {children}
    </div>
  );
}
