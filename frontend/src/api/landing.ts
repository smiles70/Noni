/**
 * Landing page API client.
 * Consumes /api/landing/page (landing-page copy, per ADR 0006).
 */
import axios from "axios";

const API_BASE = "http://127.0.0.1:8000";

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
  const res = await axios.get<LandingPageContent>(`${API_BASE}/api/landing/page`); // noqa: raw-axios-allowed
  return res.data;
}
