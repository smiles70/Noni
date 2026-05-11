"""UI State Envelope — the backend-approved contract for any renderable screen.

Per ADR 0019 and `docs/library/CONTRACT.md` (Section IV.A), the React frontend
may render ONLY backend-approved envelopes. Any envelope that does not
explicitly name its state, authorized components, interaction limits, layout
constraints, and transition permissions cannot render.

This is a pure data contract. No behavior lives here.
"""

from enum import Enum
from typing import List
from pydantic import BaseModel, ConfigDict, Field


class AuthorizedComponent(str, Enum):
    """The V1 component inventory (CONTRACT Section I.D).

    No other components may be rendered. Expansion requires a new ADR
    per CONTRACT Section VI.
    """

    HEADING = "Heading"
    BODY = "Body"
    BUTTON = "Button"
    CARD = "Card"
    FIELD = "Field"
    LIST = "List"
    DIVIDER = "Divider"
    INDICATOR = "Indicator"
    CONFIRM_DIALOG = "ConfirmDialog"
    PENDING_BANNER = "PendingBanner"
    BLOCKED_NOTICE = "BlockedNotice"


class InteractionLimits(BaseModel):
    """Per-state interaction density ceilings (CONTRACT Section I.F).

    Defaults are the contract's absolute maxima. Individual states MAY be
    more restrictive but MUST NOT be more permissive.
    """

    model_config = ConfigDict(extra="forbid")

    max_primary_actions: int = Field(default=5, ge=0, le=5)
    max_irreversible_actions: int = Field(default=1, ge=0, le=1)
    max_highlighted_recommendations: int = Field(default=1, ge=0, le=1)
    max_visible_text_levels: int = Field(default=3, ge=1, le=3)


class LayoutConstraints(BaseModel):
    """Layout rules the frontend must honor for this state
    (CONTRACT Section I.B).
    """

    model_config = ConfigDict(extra="forbid")

    grid_base_px: int = Field(default=8, description="Spacing grid base unit.")
    allowed_spacing_px: List[int] = Field(
        default_factory=lambda: [4, 8, 16, 24, 32, 48],
        description="The complete set of permitted spacing values.",
    )
    spatial_stability: bool = Field(
        default=True,
        description="Element positions persist across states and sessions.",
    )
    reflow_permitted: bool = Field(
        default=False,
        description="Reflow-driven rearrangement is prohibited by contract.",
    )


class TransitionPermission(BaseModel):
    """A single permitted transition from this state to another.

    The absence of a transition in this list means the frontend MUST NOT
    attempt it. Render Guards fail closed on unauthorized transitions.
    """

    model_config = ConfigDict(extra="forbid")

    to_state_id: str
    requires_confirmation: bool = Field(
        default=False,
        description="True for any irreversible or state-changing action.",
    )
    confirmation_copy: str | None = Field(
        default=None,
        description=(
            "If requires_confirmation, must follow the pattern: "
            "'This will change [X]. You can continue or go back.'"
        ),
    )


class UIStateEnvelope(BaseModel):
    """The authoritative envelope for a renderable screen.

    Undefined states MUST NOT render (CONTRACT Section IV.A).
    """

    model_config = ConfigDict(extra="forbid")

    state_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for this UI state.",
    )
    authorized_components: List[AuthorizedComponent] = Field(
        ...,
        min_length=1,
        description="Components the frontend may render for this state.",
    )
    interaction_limits: InteractionLimits = Field(default_factory=InteractionLimits)
    layout_constraints: LayoutConstraints = Field(default_factory=LayoutConstraints)
    transition_permissions: List[TransitionPermission] = Field(default_factory=list)


# ---- Registry of defined envelopes ------------------------------------------
#
# Each envelope corresponds to a real, renderable screen. The frontend
# resolves a screen by calling `/api/ui-envelope/{state_id}` and rendering
# only the components and transitions named here. Undefined states 404.
#
# Adding a new screen = adding a new envelope here (and tests in
# backend/tests/test_ui_state_envelope.py).


_LANDING_INTRO_ENVELOPE = UIStateEnvelope(
    state_id="landing.intro",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.DIVIDER,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=2,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=2,
    ),
    transition_permissions=[
        TransitionPermission(
            to_state_id="landing.first_win",
            requires_confirmation=False,
        ),
    ],
)


# The full landing page (LandingPage.tsx). Richer than the intro card:
# multiple sections, CTA buttons, and a single highlighted next-step.
# PendingBanner and BlockedNotice are included so the page has authorized
# components for loading and error states (B3 frontend migration).
_LANDING_PAGE_ENVELOPE = UIStateEnvelope(
    state_id="landing.page",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.CARD,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.LIST,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=3,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=3,
    ),
    transition_permissions=[
        TransitionPermission(
            to_state_id="landing.first_win",
            requires_confirmation=False,
        ),
    ],
)


# Sign-up -> First Safe Win (Golden Flow Steps 4-6).
# Step 4 invitation: low-density, reversible choice options only.
# Step 5 guided interaction: single guided action.
# Step 6 first safe win: reflection card, no required action.
_LANDING_FIRST_WIN_ENVELOPE = UIStateEnvelope(
    state_id="landing.first_win",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.CARD,
        AuthorizedComponent.FIELD,
        AuthorizedComponent.LIST,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.PENDING_BANNER,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=3,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=3,
    ),
    transition_permissions=[
        TransitionPermission(
            to_state_id="curriculum.unit",
            requires_confirmation=False,
        ),
    ],
)


# Curriculum unit page — the renderer used by Module 1 (and the same
# component used for Modules 2-5 once they ship as renderable screens).
# Per ADR 0001, curriculum progression is sequenced by user agency, so
# the only primary action here is the user-driven "next" advance.
_CURRICULUM_UNIT_ENVELOPE = UIStateEnvelope(
    state_id="curriculum.unit",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.CARD,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.INDICATOR,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=2,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=3,
    ),
    transition_permissions=[
        TransitionPermission(
            to_state_id="curriculum.unit",
            requires_confirmation=False,
        ),
    ],
)


# Account / billing screens (Sprint A8). Each is a single-purpose page.

_ACCOUNT_SIGNIN_ENVELOPE = UIStateEnvelope(
    state_id="account.signin",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.FIELD,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=2,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=2,
    ),
    transition_permissions=[
        TransitionPermission(to_state_id="account.settings"),
        TransitionPermission(to_state_id="account.paywall"),
        TransitionPermission(to_state_id="landing.page"),
    ],
)


_ACCOUNT_PAYWALL_ENVELOPE = UIStateEnvelope(
    state_id="account.paywall",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.CARD,
        AuthorizedComponent.LIST,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=3,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=2,
    ),
    transition_permissions=[
        TransitionPermission(to_state_id="account.gift_redeem"),
        TransitionPermission(to_state_id="curriculum.unit"),
        TransitionPermission(to_state_id="landing.page"),
    ],
)


_ACCOUNT_GIFT_REDEEM_ENVELOPE = UIStateEnvelope(
    state_id="account.gift_redeem",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.FIELD,
        AuthorizedComponent.CARD,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=2,
        max_irreversible_actions=0,
        max_highlighted_recommendations=1,
        max_visible_text_levels=2,
    ),
    transition_permissions=[
        TransitionPermission(to_state_id="curriculum.unit"),
        TransitionPermission(to_state_id="account.paywall"),
    ],
)


# Settings page hosts the irreversible Delete Account action, so it permits
# exactly one irreversible action and requires confirmation copy.
_ACCOUNT_SETTINGS_ENVELOPE = UIStateEnvelope(
    state_id="account.settings",
    authorized_components=[
        AuthorizedComponent.HEADING,
        AuthorizedComponent.BODY,
        AuthorizedComponent.BUTTON,
        AuthorizedComponent.CARD,
        AuthorizedComponent.LIST,
        AuthorizedComponent.DIVIDER,
        AuthorizedComponent.CONFIRM_DIALOG,
        AuthorizedComponent.PENDING_BANNER,
        AuthorizedComponent.BLOCKED_NOTICE,
    ],
    interaction_limits=InteractionLimits(
        max_primary_actions=3,
        max_irreversible_actions=1,
        max_highlighted_recommendations=0,
        max_visible_text_levels=2,
    ),
    transition_permissions=[
        TransitionPermission(
            to_state_id="account.deleted",
            requires_confirmation=True,
            confirmation_copy=(
                "This will change your account access. " "You can continue or go back."
            ),
        ),
        TransitionPermission(to_state_id="landing.page"),
    ],
)


ENVELOPES: dict[str, UIStateEnvelope] = {
    _LANDING_INTRO_ENVELOPE.state_id: _LANDING_INTRO_ENVELOPE,
    _LANDING_PAGE_ENVELOPE.state_id: _LANDING_PAGE_ENVELOPE,
    _LANDING_FIRST_WIN_ENVELOPE.state_id: _LANDING_FIRST_WIN_ENVELOPE,
    _CURRICULUM_UNIT_ENVELOPE.state_id: _CURRICULUM_UNIT_ENVELOPE,
    _ACCOUNT_SIGNIN_ENVELOPE.state_id: _ACCOUNT_SIGNIN_ENVELOPE,
    _ACCOUNT_PAYWALL_ENVELOPE.state_id: _ACCOUNT_PAYWALL_ENVELOPE,
    _ACCOUNT_GIFT_REDEEM_ENVELOPE.state_id: _ACCOUNT_GIFT_REDEEM_ENVELOPE,
    _ACCOUNT_SETTINGS_ENVELOPE.state_id: _ACCOUNT_SETTINGS_ENVELOPE,
}


def get_envelope(state_id: str) -> UIStateEnvelope | None:
    """Return the envelope for a state, or None if undefined."""
    return ENVELOPES.get(state_id)
