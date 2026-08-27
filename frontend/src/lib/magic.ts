import { Magic } from "magic-sdk";
import { AUTH_PROVIDER, MAGIC_PUBLISHABLE_KEY } from "./env";

/**
 * Magic SDK client. Null when the app is in mock mode or the publishable
 * key is not configured. Always null during SSR/build.
 */
export const magic =
  AUTH_PROVIDER === "magic" &&
  typeof window !== "undefined" &&
  MAGIC_PUBLISHABLE_KEY
    ? new Magic(MAGIC_PUBLISHABLE_KEY)
    : null;
