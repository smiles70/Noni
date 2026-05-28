/**
 * UI State Envelope API client.
 *
 * Per ADR 0019 and CONTRACT Section IV.A, the frontend resolves a screen
 * by fetching its envelope from the backend. Undefined states 404 — the
 * caller must render a BlockedNotice via RenderGuard, never guess.
 */
import type { UIStateEnvelope } from "../design/envelope";
import { API_BASE_URL } from "./client";

const API_BASE = API_BASE_URL;

export async function loadEnvelope(stateId: string): Promise<UIStateEnvelope> {
  const res = await fetch(`${API_BASE}/api/ui-envelope/${stateId}`);
  if (!res.ok) {
    throw new Error(`Envelope load failed: ${res.status}`);
  }
  return res.json() as Promise<UIStateEnvelope>;
}
