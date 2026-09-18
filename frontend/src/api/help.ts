/**
 * Learner help API — the "Call me" callback (learner-help-channel
 * intake). POST /api/v1/help/callback asks the backend to ring the
 * learner back via the Retell outbound agent.
 *
 * Auth (ADR 0024): uses the centralized `apiClient` so the Bearer
 * interceptor attaches the signed-in learner's token — the backend
 * files the callback against their account email.
 */
import { apiClient } from "./client";

export interface CallbackResponse {
  status: string;
  calling: boolean;
}

export async function requestCallback(
  phone: string,
  context?: string,
): Promise<CallbackResponse> {
  const res = await apiClient.post<CallbackResponse>("/api/v1/help/callback", {
    phone,
    context: context ?? null,
  });
  return res.data;
}
