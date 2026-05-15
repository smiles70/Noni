/**
 * Auth API client.
 *
 * The session cookie is HTTP-only + SameSite=Lax + Secure (in prod). The
 * browser sends it automatically; we just need `withCredentials: true` on
 * every call. See ADR 0023.
 *
 * Mock provider: `credential = "mock:<email>"` — used in dev/tests only.
 * Clerk provider (post-ADR-0024): `credential = <Clerk session token>`.
 */
import axios from "axios";

// API base URL. Must match the host the backend session cookie is set
// on; using "localhost" keeps the cookie usable across XHR. Override
// with VITE_API_BASE_URL if deploying split origins.
interface ImportMetaEnvShape {
  VITE_API_BASE_URL?: string;
}
const _env: ImportMetaEnvShape =
  (import.meta as unknown as { env?: ImportMetaEnvShape }).env ?? {};

export const API_BASE_URL: string =
  (_env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/+$/, "");

const client = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export interface WhoAmIResponse {
  account_id: string;
  email: string | null;
  has_active_session: boolean;
}

export async function signIn(credential: string): Promise<WhoAmIResponse> {
  const res = await client.post<WhoAmIResponse>("/auth/callback", { credential });
  return res.data;
}

export async function signOut(): Promise<void> {
  await client.post("/auth/signout");
}

export async function whoami(): Promise<WhoAmIResponse | null> {
  try {
    const res = await client.get<WhoAmIResponse>("/auth/whoami");
    return res.data;
  } catch (e: unknown) {
    if (axios.isAxiosError(e) && e.response?.status === 401) return null;
    throw e;
  }
}

export async function deleteAccount(): Promise<void> {
  await client.post("/me/delete");
}

export async function cancelDeletion(): Promise<void> {
  await client.post("/me/delete/cancel");
}
