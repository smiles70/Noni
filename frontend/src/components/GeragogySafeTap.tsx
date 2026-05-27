import { ReactNode, cloneElement, isValidElement } from "react";
import { useTouchTargetSize } from "../hooks/useTouchTargetSize";

interface SafeTapProps {
  children: ReactNode;
}

export function GeragogySafeTap({ children }: SafeTapProps) {
  const { minWidth, minHeight } = useTouchTargetSize();

  if (isValidElement(children)) {
    return cloneElement(children, {
      style: {
        ...(children.props.style || {}),
        minWidth,
        minHeight,
      },
    });
  }

  return (
    <div
      style={{
        minWidth,
        minHeight,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {children}
    </div>
  );
}
