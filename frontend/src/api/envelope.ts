/**
 * UI State Envelope API client.
 *
 * Per ADR 0019 and CONTRACT Section IV.A, the frontend resolves a screen
 * by fetching its envelope from the backend. Undefined states 404 — the
 * caller must render a BlockedNotice via RenderGuard, never guess.
 */
import axios from "axios";
import type { UIStateEnvelope } from "../design/envelope";

const API_BASE = "http://127.0.0.1:8000";

export async function loadEnvelope(stateId: string): Promise<UIStateEnvelope> {
  const res = await axios.get<UIStateEnvelope>(
    `${API_BASE}/api/ui-envelope/${stateId}`,
  );
  return res.data;
}
