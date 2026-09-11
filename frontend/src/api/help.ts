import { apiClient } from "./client";

export type HelpContext = "caregiver" | "facility";

export type CategoryId =
  | "buying_gift"
  | "payment_issue"
  | "gift_not_received"
  | "redeeming_gift"
  | "managing_recipient_access"
  | "something_else"
  | "partnership_inquiry"
  | "licensing_and_seats"
  | "onboarding_staff"
  | "technical_setup"
  | "billing_and_invoice"
  | "existing_account_issue";

export interface Category {
  id: CategoryId;
  label: string;
  severity: "P0" | "P1" | "P2" | "P3";
  initialResponseTime: string;
}

export const CAREGIVER_CATEGORIES: Category[] = [
  {
    id: "buying_gift",
    label: "Buying as gift",
    severity: "P3",
    initialResponseTime: "one week",
  },
  {
    id: "payment_issue",
    label: "Payment issue",
    severity: "P1",
    initialResponseTime: "8 hours",
  },
  {
    id: "gift_not_received",
    label: "Gift not received",
    severity: "P1",
    initialResponseTime: "8 hours",
  },
  {
    id: "redeeming_gift",
    label: "Redeeming a gift",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "managing_recipient_access",
    label: "Managing recipient access",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "something_else",
    label: "Something else",
    severity: "P3",
    initialResponseTime: "one week",
  },
];

export const FACILITY_CATEGORIES: Category[] = [
  {
    id: "partnership_inquiry",
    label: "Partnership inquiry",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "licensing_and_seats",
    label: "Licensing and seats",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "onboarding_staff",
    label: "Onboarding staff",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "technical_setup",
    label: "Technical setup",
    severity: "P1",
    initialResponseTime: "8 hours",
  },
  {
    id: "billing_and_invoice",
    label: "Billing and invoice",
    severity: "P1",
    initialResponseTime: "8 hours",
  },
  {
    id: "existing_account_issue",
    label: "Existing account issue",
    severity: "P2",
    initialResponseTime: "48 hours",
  },
  {
    id: "something_else",
    label: "Something else",
    severity: "P3",
    initialResponseTime: "one week",
  },
];

export const CATEGORIES_BY_CONTEXT: Record<HelpContext, Category[]> = {
  caregiver: CAREGIVER_CATEGORIES,
  facility: FACILITY_CATEGORIES,
};

export function categoryById(
  context: HelpContext,
  id: CategoryId,
): Category | undefined {
  return CATEGORIES_BY_CONTEXT[context].find((c) => c.id === id);
}

export function isCategoryForContext(
  context: HelpContext,
  id: string,
): boolean {
  return CATEGORIES_BY_CONTEXT[context].some((c) => c.id === id);
}

export interface HelpRequestBody {
  context: HelpContext;
  category: string;
  message: string;
  reply_email?: string;
  request_id: string;
  page_path: string;
}

export interface HelpRequestResponse {
  id: string;
  request_id: string;
  context: string;
  category: string;
  sub_category: string | null;
  severity: string | null;
  reply_email: string | null;
  message: string;
  page_path: string | null;
  status: string;
  n8n_status: string;
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
  category: CategoryId,
  message: string,
  pagePath: string,
  replyEmail?: string,
): Promise<HelpRequestResponse> {
  const res = await apiClient.post<HelpRequestResponse>(
    "/api/v1/help/requests",
    {
      context,
      category,
      message,
      reply_email: replyEmail,
      request_id: generateRequestId(),
      page_path: pagePath,
    },
  );
  return res.data;
}
