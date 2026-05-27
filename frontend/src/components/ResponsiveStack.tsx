import { ReactNode } from "react";
import { useViewportContext } from "../context/ViewportContext";
import { SPACING } from "../styles/responsiveTokens";

interface StackProps {
  children: ReactNode;
}

export function ResponsiveStack({ children }: StackProps) {
  const { breakpoint } = useViewportContext();

  return (
    <div
      style={{
        display: "flex",
        flexDirection: breakpoint === "mobile" ? "column" : "row",
        gap: SPACING[breakpoint].md,
        width: "100%",
      }}
    >
      {children}
    </div>
  );
}
