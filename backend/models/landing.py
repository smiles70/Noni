"""Golden Landing Flow data model.

Canonical structure for the 8-step first-visit experience.
See `docs/flows/golden-landing-flow.md` for the full spec and
`docs/decisions/0001-landing-flow.md` for the architecture rationale.

Display-copy fields (`display_title`, `display_body`, `action_label`)
are intentionally `None` here. Final user-facing copy belongs to a
later "Copy & Visual Design" sprint and must not be set in this module.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class LandingStep(BaseModel):
    id: str
    sequence: int = Field(ge=0, le=7)
    name: str
    user_state: List[str]
    system_responsibility: List[str]
    user_agency: List[str]
    exit_safety: str
    requires_user_action: bool
    exit_always_safe: bool = True

    # To be set in a later sprint after copy is finalized.
    display_title: Optional[str] = None
    display_body: Optional[List[str]] = None
    action_label: Optional[str] = None


LANDING_STEPS: List[LandingStep] = [
    LandingStep(
        id="step-0",
        sequence=0,
        name="Arrival",
        user_state=[
            "Curious or uncertain",
            "Possible anxiety about AI or doing something wrong",
            "No intent to commit yet",
        ],
        system_responsibility=[
            "Require nothing",
            "Demand nothing",
            "Explain nothing yet",
        ],
        user_agency=[
            "Can leave immediately with no loss",
            "Has not been assessed, tracked, or obligated",
        ],
        exit_safety="Full exit, no penalty",
        requires_user_action=False,
    ),
    LandingStep(
        id="step-1",
        sequence=1,
        name="What This Is",
        user_state=[
            "Wants to know: What is this?",
            "Assessing risk, tone, and credibility",
        ],
        system_responsibility=[
            "Explain what Noni is in plain language",
            "Clarify what it does and does not do",
            "Set calm expectations",
        ],
        user_agency=[
            "Passive reading only",
            "No decisions required",
        ],
        exit_safety="Full exit, no penalty",
        requires_user_action=False,
    ),
    LandingStep(
        id="step-2",
        sequence=2,
        name="Is This For Me",
        user_state=[
            "Internally evaluating relevance",
            "Comparing this to past technology experiences",
        ],
        system_responsibility=[
            "Describe who Noni is designed for",
            "Normalize uncertainty and lack of experience",
            "Explicitly remove any expectation of prior knowledge",
        ],
        user_agency=[
            "User decides privately if this feels appropriate",
            "No input required",
        ],
        exit_safety="Full exit, no penalty",
        requires_user_action=False,
    ),
    LandingStep(
        id="step-3",
        sequence=3,
        name="Safety and Control",
        user_state=[
            "Concerned about mistakes, privacy, or being overwhelmed",
        ],
        system_responsibility=[
            "State clearly: nothing happens automatically",
            "State clearly: all actions are previewed",
            "State clearly: stopping is always allowed",
            "Reinforce user authority",
        ],
        user_agency=[
            "Permission-based continuation only",
        ],
        exit_safety="Full exit, no penalty",
        requires_user_action=False,
    ),
    LandingStep(
        id="step-4",
        sequence=4,
        name="Low-Commitment Choice",
        user_state=[
            "Ready to explore, but not to commit",
        ],
        system_responsibility=[
            "Offer a gentle option to continue",
            "Emphasize reversibility and lack of obligation",
        ],
        user_agency=[
            "Optional choice to explore further",
            "First explicit action, but still low-stakes",
        ],
        exit_safety="Declining has no downside; no data dependency created",
        requires_user_action=True,
    ),
    LandingStep(
        id="step-5",
        sequence=5,
        name="First Guided Interaction",
        user_state=[
            "Slightly engaged",
            "Testing whether the system feels safe",
        ],
        system_responsibility=[
            "Provide a single, simple, guided interaction",
            "No branching",
            "No complex decisions",
            "No time pressure",
        ],
        user_agency=[
            "User sees Claude respond in a controlled, explain-as-you-go way",
            "Nothing is asked of the user except observation or a simple acknowledgment",
        ],
        exit_safety="User can stop immediately; nothing persists unless they choose later",
        requires_user_action=True,
    ),
    LandingStep(
        id="step-6",
        sequence=6,
        name="First Safe Win",
        user_state=[
            "Experiencing usefulness for the first time",
            "Beginning to form confidence",
        ],
        system_responsibility=[
            "Make the value explicit (this is what learning with Noni feels like)",
            "Reflect success back to the user without praise or judgment",
        ],
        user_agency=[
            "Understanding achieved",
            "No identity threat",
            "No dependency created",
        ],
        exit_safety="User can leave feeling informed, not enrolled",
        requires_user_action=False,
    ),
    LandingStep(
        id="step-7",
        sequence=7,
        name="Optional Continuation",
        user_state=[
            "Calm, informed, confident enough to decide",
        ],
        system_responsibility=[
            "Offer next steps only now",
            "Make clear that learning can remain gradual",
        ],
        user_agency=[
            "Choice to continue, pause, or leave",
            "All options equally valid",
        ],
        exit_safety="Full exit remains safe and respected",
        requires_user_action=True,
    ),
]


def get_step(step_id: str) -> Optional[LandingStep]:
    """Lookup helper. Returns None if step_id is unknown."""
    for s in LANDING_STEPS:
        if s.id == step_id:
            return s
    return None
