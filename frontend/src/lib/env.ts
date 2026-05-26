interface ImportMetaEnv {
  VITE_API_BASE_URL?: string;
  VITE_AUTH_PROVIDER?: string;
  VITE_CLERK_PUBLISHABLE_KEY?: string;
  VITE_LOG_LEVEL?: string;
  DEV?: boolean;
  PROD?: boolean;
}

const _env: ImportMetaEnv =
  (import.meta as unknown as { env?: ImportMetaEnv }).env ?? {};

export const API_BASE_URL: string = (
  _env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

export const AUTH_PROVIDER: string = _env.VITE_AUTH_PROVIDER ?? "mock";

export const CLERK_PUBLISHABLE_KEY: string =
  _env.VITE_CLERK_PUBLISHABLE_KEY ?? "";

export const LOG_LEVEL: string = _env.VITE_LOG_LEVEL ?? "info";

export const IS_DEV: boolean = _env.DEV === true;

export const IS_PROD: boolean = _env.PROD === true;
