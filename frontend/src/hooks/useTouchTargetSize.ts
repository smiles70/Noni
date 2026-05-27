import { useViewportContext } from "../context/ViewportContext";
import { MIN_TOUCH_TARGET } from "../styles/responsiveTokens";

export interface TouchTargetSize {
  minWidth: number;
  minHeight: number;
}

export function useTouchTargetSize(): TouchTargetSize {
  const { breakpoint } = useViewportContext();
  const size = MIN_TOUCH_TARGET[breakpoint];

  return { minWidth: size, minHeight: size };
}
