"""Tests for the UI State Envelope contract and endpoint.

Verifies the contract enforcement described in ADR 0019 and
`docs/library/CONTRACT.md` Section IV.A:

  - Defined states return a complete envelope.
  - Undefined states return 404 (frontend must not render).
  - Schema rejects out-of-contract values (extra fields, over-limits).
  - V1 component inventory is enforced (no unauthorized components).
  - Spacing scale is the closed set {4, 8, 16, 24, 32, 48}.
"""

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.app.main import app
from backend.models.ui_state_envelope import (
    AuthorizedComponent,
    InteractionLimits,
    LayoutConstraints,
    TransitionPermission,
    UIStateEnvelope,
    get_envelope,
)


# Router is registered in backend/app/main.py under /api/ui-envelope.
client = TestClient(app)


# ---- Schema-level tests -----------------------------------------------------


def test_envelope_requires_state_id():
    with pytest.raises(ValidationError):
        UIStateEnvelope(
            state_id="",
            authorized_components=[AuthorizedComponent.BODY],
        )


def test_envelope_requires_at_least_one_authorized_component():
    with pytest.raises(ValidationError):
        UIStateEnvelope(state_id="x", authorized_components=[])


def test_envelope_rejects_extra_fields():
    with pytest.raises(ValidationError):
        UIStateEnvelope(
            state_id="x",
            authorized_components=[AuthorizedComponent.BODY],
            mystery_field="not allowed",  # type: ignore[call-arg]
        )


def test_authorized_components_enum_is_exactly_v1_inventory():
    """CONTRACT Section I.D: exactly 11 components in V1."""
    assert len(list(AuthorizedComponent)) == 11
    expected = {
        "Heading",
        "Body",
        "Button",
        "Card",
        "Field",
        "List",
        "Divider",
        "Indicator",
        "ConfirmDialog",
        "PendingBanner",
        "BlockedNotice",
    }
    assert {c.value for c in AuthorizedComponent} == expected


def test_authorized_components_rejects_unknown():
    with pytest.raises(ValidationError):
        UIStateEnvelope(
            state_id="x",
            authorized_components=["Carousel"],  # type: ignore[list-item]
        )


# ---- Interaction limits -----------------------------------------------------


def test_interaction_limits_ceiling_primary_actions():
    """CONTRACT Section I.F: ≤5 primary actions."""
    with pytest.raises(ValidationError):
        InteractionLimits(max_primary_actions=6)


def test_interaction_limits_ceiling_irreversible():
    """CONTRACT Section I.F: ≤1 irreversible action."""
    with pytest.raises(ValidationError):
        InteractionLimits(max_irreversible_actions=2)


def test_interaction_limits_ceiling_highlighted():
    with pytest.raises(ValidationError):
        InteractionLimits(max_highlighted_recommendations=2)


def test_interaction_limits_ceiling_text_levels():
    """CONTRACT Section I.C: max 3 visible text levels."""
    with pytest.raises(ValidationError):
        InteractionLimits(max_visible_text_levels=4)


def test_interaction_limits_defaults_match_contract_maxima():
    limits = InteractionLimits()
    assert limits.max_primary_actions == 5
    assert limits.max_irreversible_actions == 1
    assert limits.max_highlighted_recommendations == 1
    assert limits.max_visible_text_levels == 3


# ---- Layout constraints -----------------------------------------------------


def test_layout_constraints_default_spacing_is_closed_set():
    """CONTRACT Section I.B: spacing = {4, 8, 16, 24, 32, 48}."""
    layout = LayoutConstraints()
    assert layout.allowed_spacing_px == [4, 8, 16, 24, 32, 48]
    assert layout.grid_base_px == 8


def test_layout_constraints_default_spatial_stability_on():
    layout = LayoutConstraints()
    assert layout.spatial_stability is True
    assert layout.reflow_permitted is False


# ---- Transition permissions -------------------------------------------------


def test_transition_permission_minimal():
    t = TransitionPermission(to_state_id="other.state")
    assert t.requires_confirmation is False
    assert t.confirmation_copy is None


def test_transition_permission_rejects_extras():
    with pytest.raises(ValidationError):
        TransitionPermission(
            to_state_id="other.state",
            magic="nope",  # type: ignore[call-arg]
        )


# ---- Registry / lookup ------------------------------------------------------


def test_registry_returns_none_for_undefined():
    assert get_envelope("nonexistent.state") is None


def test_registry_returns_envelope_for_seeded_state():
    env = get_envelope("landing.intro")
    assert env is not None
    assert env.state_id == "landing.intro"
    # Only V1 components used.
    for c in env.authorized_components:
        assert c in AuthorizedComponent


# ---- Endpoint tests ---------------------------------------------------------


def test_endpoint_returns_envelope_for_known_state():
    response = client.get("/api/ui-envelope/landing.intro")
    assert response.status_code == 200
    body = response.json()
    assert body["state_id"] == "landing.intro"
    assert "authorized_components" in body
    assert "interaction_limits" in body
    assert "layout_constraints" in body
    assert "transition_permissions" in body


def test_endpoint_returns_404_for_undefined_state():
    """CONTRACT Section IV.A: undefined states MUST NOT render."""
    response = client.get("/api/ui-envelope/does.not.exist")
    assert response.status_code == 404
    assert "undefined" in response.json()["detail"].lower()


def test_endpoint_payload_respects_contract_maxima():
    response = client.get("/api/ui-envelope/landing.intro")
    body = response.json()
    limits = body["interaction_limits"]
    assert limits["max_primary_actions"] <= 5
    assert limits["max_irreversible_actions"] <= 1
    assert limits["max_highlighted_recommendations"] <= 1
    assert limits["max_visible_text_levels"] <= 3
    assert body["layout_constraints"]["allowed_spacing_px"] == [4, 8, 16, 24, 32, 48]


# ---- B2: seeded envelopes for real screens ----------------------------------


@pytest.mark.parametrize(
    "state_id",
    [
        "landing.intro",
        "landing.page",
        "landing.first_win",
        "curriculum.unit",
    ],
)
def test_seeded_envelope_resolves(state_id):
    """Every real screen has a defined envelope."""
    env = get_envelope(state_id)
    assert env is not None
    assert env.state_id == state_id


@pytest.mark.parametrize(
    "state_id",
    [
        "landing.intro",
        "landing.page",
        "landing.first_win",
        "curriculum.unit",
    ],
)
def test_seeded_envelope_respects_contract_ceilings(state_id):
    """CONTRACT Section I.F: every envelope honors the global maxima."""
    env = get_envelope(state_id)
    assert env is not None
    assert env.interaction_limits.max_primary_actions <= 5
    assert env.interaction_limits.max_irreversible_actions <= 1
    assert env.interaction_limits.max_highlighted_recommendations <= 1
    assert env.interaction_limits.max_visible_text_levels <= 3


@pytest.mark.parametrize(
    "state_id",
    [
        "landing.intro",
        "landing.page",
        "landing.first_win",
        "curriculum.unit",
    ],
)
def test_seeded_envelope_uses_only_v1_components(state_id):
    """CONTRACT Section I.D: only V1 component inventory."""
    env = get_envelope(state_id)
    assert env is not None
    for c in env.authorized_components:
        assert c in AuthorizedComponent


@pytest.mark.parametrize(
    "state_id",
    [
        "landing.page",
        "landing.first_win",
        "curriculum.unit",
    ],
)
def test_seeded_envelope_endpoint_returns_200(state_id):
    response = client.get(f"/api/ui-envelope/{state_id}")
    assert response.status_code == 200
    assert response.json()["state_id"] == state_id


def test_landing_first_win_transitions_to_curriculum():
    """The first-win flow ends by handing off to the curriculum unit page."""
    env = get_envelope("landing.first_win")
    assert env is not None
    target_ids = {t.to_state_id for t in env.transition_permissions}
    assert "curriculum.unit" in target_ids


def test_curriculum_unit_self_loops_for_next_advance():
    """Per ADR 0001, advance is user-driven; the unit transitions to itself
    to render the next unit's content within the same envelope."""
    env = get_envelope("curriculum.unit")
    assert env is not None
    target_ids = {t.to_state_id for t in env.transition_permissions}
    assert "curriculum.unit" in target_ids


def test_every_transition_targets_a_defined_envelope():
    """Closed-world: no transition may point at an undefined state."""
    from backend.models.ui_state_envelope import ENVELOPES

    for env in ENVELOPES.values():
        for t in env.transition_permissions:
            assert get_envelope(t.to_state_id) is not None, (
                f"Envelope '{env.state_id}' has a transition to undefined "
                f"state '{t.to_state_id}'."
            )
