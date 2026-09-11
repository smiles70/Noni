import { apiClient } from "./client";

export type HelpContext = "caregiver" | "facility";

export const CAREGIVER_CATEGORIES = [
  "Buying as a gift",
  "Gift delivery question",
  "Payment issue",
  "Other",
];

export const FACILITY_CATEGORIES = [
  "Partnership question",
  "Pricing",
  "Implementation support",
  "Technical issue",
  "Other",
];

export const CATEGORIES_BY_CONTEXT: Record<HelpContext, string[]> = {
  caregiver: CAREGIVER_CATEGORIES,
  facility: FACILITY_CATEGORIES,
};

export interface HelpRequestBody {
  context: HelpContext;
  category: string;
  message: string;
  email?: string;
  request_id: string;
  page_path: string;
}

export interface HelpRequestResponse {
  id: string;
  request_id: string;
  context: string;
  category: string;
  email: string | null;
  message: string;
  page_path: string | null;
  status: string;
  created_at: string;
}

function generateRequestId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;
}

export async function submitHelpRequest(
  context: HelpContext,
  category: string,
  message: string,
  pagePath: string,
  email?: string,
): Promise<HelpRequestResponse> {
  const res = await apiClient.post<HelpRequestResponse>(
    "/api/v1/help/requests",
    {
      context,
      category,
      message,
      email,
      request_id: generateRequestId(),
      page_path: pagePath,
    },
  );
  return res.data;
}
