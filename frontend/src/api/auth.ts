/**
 * Auth API client.
 *
 * The session cookie is HTTP-only + SameSite=Lax + Secure (in prod). The
 * browser sends it automatically; we just need `withCredentials: true` on
 * every call. See ADR 0023.
 *
 * Mock provider: `credential = "mock:<email>"` — used in dev/tests only.
 * Supabase provider: `credential = <Supabase access token>`.
 */
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE,
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
