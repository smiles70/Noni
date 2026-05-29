/**
 * Route guard: redirects unauthenticated users to /signin with a
 * ?redirect= param so they are forwarded after successful authentication.
 *
 * Series A Step 1 (P3/P6/P7): replaces the in-memory GATED_VIEWS set
 * with declarative route-level auth gating.
 */
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthProvider";

interface Props {
  children: React.ReactNode;
}

export default function RequireAuth({ children }: Props) {
  const { state } = useAuth();
  const location = useLocation();
  const isReady = state?.status === "READY";

  if (!isReady) {
    // Preserve the current path so we can redirect back after sign-in.
    const redirect = encodeURIComponent(location.pathname + location.search);
    return <Navigate to={`/signin?redirect=${redirect}`} replace />;
  }

  return <>{children}</>;
}
