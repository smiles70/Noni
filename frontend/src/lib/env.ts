/// <reference types="vite/client" />

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

// Auth provider: "mock" for dev/tests; "magic" for production.
// See ADR 0027 and docs/deferred-decisions.md.
export const AUTH_PROVIDER: string = (
  import.meta.env.VITE_AUTH_PROVIDER ?? "mock"
)
  .trim()
  .toLowerCase();

export const MAGIC_PUBLISHABLE_KEY: string = (
  import.meta.env.VITE_MAGIC_PUBLISHABLE_KEY ?? ""
).trim();

export const LOG_LEVEL: string = import.meta.env.VITE_LOG_LEVEL ?? "info";

// Retell website widget (ADR 0032). Public key is safe for frontend use —
// it is domain-locked in the Retell dashboard. Unset => ChatWidget no-ops.
export const RETELL_PUBLIC_KEY: string = (
  import.meta.env.VITE_RETELL_PUBLIC_KEY ?? ""
).trim();

export const RETELL_CHAT_AGENT_ID: string = (
  import.meta.env.VITE_RETELL_CHAT_AGENT_ID ?? ""
).trim();

export const IS_DEV: boolean = import.meta.env.DEV === true;

export const IS_PROD: boolean = import.meta.env.PROD === true;
