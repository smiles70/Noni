import { createContext, useContext, ReactNode } from "react";
import { useViewport, ViewportState } from "../hooks/useViewport";

const ViewportContext = createContext<ViewportState | null>(null);

export function ViewportProvider({ children }: { children: ReactNode }) {
  const viewport = useViewport();
  return (
    <ViewportContext.Provider value={viewport}>
      {children}
    </ViewportContext.Provider>
  );
}

export function useViewportContext(): ViewportState {
  const ctx = useContext(ViewportContext);
  if (!ctx) {
    throw new Error("useViewportContext must be used within ViewportProvider");
  }
  return ctx;
}
