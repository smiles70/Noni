/**
 * UI State Envelope API client.
 *
 * Per ADR 0019 and CONTRACT Section IV.A, the frontend resolves a screen
 * by fetching its envelope from the backend. Undefined states 404 — the
 * caller must render a BlockedNotice via RenderGuard, never guess.
 */
import axios from "axios";
import type { UIStateEnvelope } from "../design/envelope";
import { API_BASE_URL } from "./client";

const API_BASE = API_BASE_URL;

export async function loadEnvelope(stateId: string): Promise<UIStateEnvelope> {
  // TODO: migrate to apiClient once the envelope endpoint is consistently
  // auth-gated; for now this is a public read.
  const res = await axios.get<UIStateEnvelope>( // noqa: raw-axios-allowed
    `${API_BASE}/api/ui-envelope/${stateId}`,
  );
  return res.data;
}
