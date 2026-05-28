/**
 * Frontend client for the Interface State Control System (ISCS).
 * The frontend ONLY consumes backend-approved UI states.
 */
import { API_BASE_URL } from "./client";

const API_BASE = API_BASE_URL;

export interface CurriculumPage {
  id: string;
  title: string;
  content: string[];
  complexity: number;
}

export interface ApprovedUIState {
  ui_state: CurriculumPage;
  stability: number;
}

export async function loadWhatIsAI(): Promise<ApprovedUIState> {
  // Public free-preview endpoint.
  const res = await fetch(`${API_BASE}/api/curriculum/what-is-ai`);
  if (!res.ok) {
    throw new Error(`What-is-AI load failed: ${res.status}`);
  }
  return res.json() as Promise<ApprovedUIState>;
}
