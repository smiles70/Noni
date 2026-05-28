/**
 * Landing page API client.
 * Consumes /api/landing/page (landing-page copy, per ADR 0006).
 */
import { API_BASE_URL } from "./client";

const API_BASE = API_BASE_URL;

export interface Hero {
  headline: string;
  subheadline: string;
}
export interface ProseSection {
  title: string;
  body: string;
}
export interface ListSection {
  title: string;
  items: string[];
}
export interface CTA {
  label: string;
  note: string;
}
export interface CallToAction {
  primary: CTA;
  secondary: CTA;
}
export interface Closing {
  body: string;
}
export interface LandingPageContent {
  hero: Hero;
  introduction: ProseSection;
  what_noni_does: ListSection;
  how_it_feels: ListSection;
  trust_and_safety: ProseSection;
  call_to_action: CallToAction;
  closing: Closing;
}

export async function loadLandingPage(): Promise<LandingPageContent> {
  // Landing page is intentionally public; no Bearer token required.
  const res = await fetch(`${API_BASE}/api/landing/page`);
  if (!res.ok) {
    throw new Error(`Landing page load failed: ${res.status}`);
  }
  return res.json() as Promise<LandingPageContent>;
}
