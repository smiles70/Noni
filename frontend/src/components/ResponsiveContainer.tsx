import { ReactNode } from "react";
import { useViewportContext } from "../context/ViewportContext";
import { MAX_CONTENT_WIDTH, SPACING } from "../styles/responsiveTokens";

interface ContainerProps {
  children: ReactNode;
}

export function ResponsiveContainer({ children }: ContainerProps) {
  const { breakpoint } = useViewportContext();

  return (
    <div
      style={{
        width: "100%",
        maxWidth: MAX_CONTENT_WIDTH[breakpoint],
        margin: "0 auto",
        padding: SPACING[breakpoint].lg,
        boxSizing: "border-box",
        minHeight: "100vh",
        overflowX: "hidden",
      }}
    >
      {children}
    </div>
  );
}
