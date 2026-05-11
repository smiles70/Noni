/**
 * UI State Envelope — frontend type contract.
 *
 * Mirrors `backend/models/ui_state_envelope.py`. The backend is the source
 * of truth; this file exists only so React components are statically typed
 * against the same shape. Any divergence is a bug.
 *
 * Source of truth: `docs/library/CONTRACT.md` Section IV.A.
 */

import type { AuthorizedComponent } from "./tokens";

export interface InteractionLimits {
  max_primary_actions: number;
  max_irreversible_actions: number;
  max_highlighted_recommendations: number;
  max_visible_text_levels: number;
}

export interface LayoutConstraints {
  grid_base_px: number;
  allowed_spacing_px: number[];
  spatial_stability: boolean;
  reflow_permitted: boolean;
}

export interface TransitionPermission {
  to_state_id: string;
  requires_confirmation: boolean;
  confirmation_copy: string | null;
}

export interface UIStateEnvelope {
  state_id: string;
  authorized_components: AuthorizedComponent[];
  interaction_limits: InteractionLimits;
  layout_constraints: LayoutConstraints;
  transition_permissions: TransitionPermission[];
}
