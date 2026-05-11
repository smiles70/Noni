/**
 * Billing & gift API client. Cookie-authenticated like auth.ts.
 * See ADR 0021.
 */
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true,
});

export interface CheckoutResponse {
  purchase_id: string;
  checkout_url: string;
  provider_session_id: string;
}

export async function startCheckout(
  productCode: string,
  isGift: boolean,
): Promise<CheckoutResponse> {
  const res = await client.post<CheckoutResponse>("/api/billing/checkout", {
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
  const res = await client.post<GiftPreview>("/api/gifts/preview", { token });
  return res.data;
}

export interface GiftClaim {
  purchase_id: string;
  product_code: string;
  granted_to_account_id: string;
}

export async function claimGift(token: string): Promise<GiftClaim> {
  const res = await client.post<GiftClaim>("/api/gifts/claim", { token });
  return res.data;
}
