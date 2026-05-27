import { useState, useEffect } from "react";

export type Breakpoint = "mobile" | "tablet" | "desktop" | "wide";

export interface ViewportState {
  width: number;
  height: number;
  breakpoint: Breakpoint;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isWide: boolean;
}

const BREAKPOINTS = {
  mobile: 0,
  tablet: 768,
  desktop: 1024,
  wide: 1440,
};

function getBreakpoint(width: number): Breakpoint {
  if (width >= BREAKPOINTS.wide) return "wide";
  if (width >= BREAKPOINTS.desktop) return "desktop";
  if (width >= BREAKPOINTS.tablet) return "tablet";
  return "mobile";
}

export function useViewport(): ViewportState {
  const safeWindow = typeof window !== "undefined";

  const [width, setWidth] = useState<number>(
    safeWindow ? window.innerWidth : 1024
  );
  const [height, setHeight] = useState<number>(
    safeWindow ? window.innerHeight : 768
  );

  useEffect(() => {
    if (!safeWindow) return;

    let ticking = false;

    function handleResize() {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          setWidth(window.innerWidth);
          setHeight(window.innerHeight);
          ticking = false;
        });
        ticking = true;
      }
    }

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [safeWindow]);

  const breakpoint = getBreakpoint(width);

  return {
    width,
    height,
    breakpoint,
    isMobile: breakpoint === "mobile",
    isTablet: breakpoint === "tablet",
    isDesktop: breakpoint === "desktop",
    isWide: breakpoint === "wide",
  };
}
