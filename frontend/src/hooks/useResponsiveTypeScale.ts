import { useViewportContext } from "../context/ViewportContext";
import { TYPE_SCALE } from "../styles/responsiveTokens";

type TextVariant = keyof typeof TYPE_SCALE.mobile;

export function useResponsiveTypeScale(variant: TextVariant): { fontSize: number } {
  const { breakpoint } = useViewportContext();
  return { fontSize: TYPE_SCALE[breakpoint][variant] };
}
