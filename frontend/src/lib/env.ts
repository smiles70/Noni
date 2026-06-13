/// <reference types="vite/client" />

export const API_BASE_URL: string = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

export const AUTH_PROVIDER: string = import.meta.env.VITE_AUTH_PROVIDER ?? "mock";

export const CLERK_PUBLISHABLE_KEY: string =
  import.meta.env.VITE_CLERK_PUBLISHABLE_KEY ?? "";

export const LOG_LEVEL: string = import.meta.env.VITE_LOG_LEVEL ?? "info";

export const IS_DEV: boolean = import.meta.env.DEV === true;

export const IS_PROD: boolean = import.meta.env.PROD === true;
