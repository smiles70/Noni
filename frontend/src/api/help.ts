/**
 * Learner help API — the "Call me" callback (learner-help-channel
 * intake). POST /api/v1/help/callback asks the backend to ring the
 * learner back via the Retell outbound agent.
 */
import { API_BASE_URL } from "../lib/env";

export interface CallbackResponse {
  status: string;
  calling: boolean;
}

export async function requestCallback(
  phone: string,
  context?: string,
): Promise<CallbackResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/help/callback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ phone, context: context ?? null }),
  });
  if (!res.ok) {
    throw new Error(`Callback request failed: ${res.status}`);
  }
  return res.json() as Promise<CallbackResponse>;
}
