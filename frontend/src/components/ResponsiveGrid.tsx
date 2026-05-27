import { ReactNode } from "react";
import { useViewportContext } from "../context/ViewportContext";
import { SPACING } from "../styles/responsiveTokens";

interface GridProps {
  children: ReactNode;
  gap?: "xs" | "sm" | "md" | "lg" | "xl";
}

export function ResponsiveGrid({ children, gap = "md" }: GridProps) {
  const { breakpoint } = useViewportContext();

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          breakpoint === "mobile"
            ? "1fr"
            : breakpoint === "tablet"
            ? "1fr 1fr"
            : "repeat(3, 1fr)",
        gap: SPACING[breakpoint][gap],
        width: "100%",
      }}
    >
      {children}
    </div>
  );
}
