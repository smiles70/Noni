/// <reference types="vite/client" />

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

// Normalised so a stray newline/space or different casing in the build-time
// env (e.g. a GitHub secret pasted as "clerk\n") cannot desync the two
// provider checks in main.tsx and auth/AuthProvider.tsx — a mismatch there
// mounts the mock tree while running the Clerk code path, crashing with
// "useAuth can only be used within <ClerkProvider>".
export const AUTH_PROVIDER: string = (
  import.meta.env.VITE_AUTH_PROVIDER ?? "mock"
).trim().toLowerCase();

export const CLERK_PUBLISHABLE_KEY: string = (
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ?? ""
).trim();

export const LOG_LEVEL: string = import.meta.env.VITE_LOG_LEVEL ?? "info";

export const IS_DEV: boolean = import.meta.env.DEV === true;

export const IS_PROD: boolean = import.meta.env.PROD === true;
