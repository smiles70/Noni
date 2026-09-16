/**
 * Site-chrome API client — backend-served footer copy.
 * Consumes /api/site/footer (see backend/api/routes/site.py).
 */
import { API_BASE_URL } from "./client";

export interface FooterLink {
  label: string;
  href: string;
}

export interface SiteFooterContent {
  tagline: string;
  nav_links: FooterLink[];
  legal_links: FooterLink[];
  mini_links: FooterLink[];
  social_links: FooterLink[];
  brand_label: string;
  copyright: string;
  /** Public "call us" line for /partners; empty = hidden. */
  contact_phone: string;
}

export async function loadFooterContent(): Promise<SiteFooterContent> {
  // Footer copy is intentionally public; no Bearer token required.
  const res = await fetch(`${API_BASE_URL}/api/site/footer`);
  if (!res.ok) {
    throw new Error(`Footer content load failed: ${res.status}`);
  }
  return res.json() as Promise<SiteFooterContent>;
}
