/**
 * Billing & gift API client.
 *
 * Auth (ADR 0024): uses the centralized `apiClient` so the Bearer
 * token is attached automatically. See ADR 0021 for billing semantics.
 */
import { apiClient } from "./client";

export interface CheckoutResponse {
  purchase_id: string;
  checkout_url: string;
  provider_session_id: string;
}

export async function startCheckout(
  productCode: string,
  isGift: boolean,
): Promise<CheckoutResponse> {
  const res = await apiClient.post<CheckoutResponse>("/api/billing/checkout", {
    product_code: productCode,
    is_gift: isGift,
  });
  return res.data;
}

export interface GiftPreview {
  valid: boolean;
  product_code: string | null;
  purchase_id: string | null;
}

export async function previewGift(token: string): Promise<GiftPreview> {
  const res = await apiClient.post<GiftPreview>("/api/gifts/preview", { token });
  return res.data;
}

export interface GiftClaim {
  purchase_id: string;
  product_code: string;
  granted_to_account_id: string;
}

export async function claimGift(token: string): Promise<GiftClaim> {
  const res = await apiClient.post<GiftClaim>("/api/gifts/claim", { token });
  return res.data;
}
