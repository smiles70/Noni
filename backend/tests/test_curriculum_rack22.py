"""Rack 2.2 — targeted branch coverage for backend/api/routes/curriculum.py."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from backend.api.routes.curriculum import _selected_id, paid_bundle_dep
from backend.app.main import app
from backend.core.database import SessionLocal
from backend.models.accounts import Account
from backend.models.billing import Product, Purchase
from backend.models.curriculum import CurriculumPage
from backend.models.curriculum_units import CurriculumUnit, TelemetryGatedUnit
from backend.models.learning import Unit
from backend.models.organizations import AccessCode, Organization, OrgLicense
from backend.services.mock_parser import MOCK_NAMESPACE


@pytest.fixture(autouse=True)
def _bypass_paid_gate():
    """Paid bundle routes are entitlement-tested elsewhere; focus is curriculum."""
    app.dependency_overrides[paid_bundle_dep] = lambda: None
    yield
    app.dependency_overrides.pop(paid_bundle_dep, None)


@pytest.fixture
def client():
    return TestClient(app)


def _fake_unit(telemetry: bool = False):
    page = CurriculumPage(
        id="rack22-page",
        title="Rack page",
        content=["content"],
        complexity=1,
    )
    cls = TelemetryGatedUnit if telemetry else CurriculumUnit
    return cls(
        id="rack22-fake",
        title="Rack fake",
        description="fake",
        pages=[page],
        max_complexity=0,
        stability_threshold=1.0,
    )


def _auth(email: str) -> dict:
    return {"Authorization": f"Bearer mock:{email}"}


def test_selected_id_branches():
    """Direct coverage for the _selected_id helper false branches."""
    assert _selected_id({"id": "abc"}) == "abc"
    assert _selected_id({"id": 123}) == "unknown"
    assert _selected_id("not-a-dict") == "unknown"
    assert _selected_id(None) == "unknown"


@pytest.mark.parametrize(
    "endpoint, getter, telemetry",
    [
        (
            "/api/v1/curriculum/units/fake",
            "backend.api.routes.curriculum.get_unit",
            False,
        ),
        (
            "/api/v1/curriculum/module-0/units/fake",
            "backend.api.routes.curriculum.get_module_0_unit",
            False,
        ),
        (
            "/api/v1/curriculum/module-2/units/fake",
            "backend.api.routes.curriculum.get_module_2_unit",
            True,
        ),
        (
            "/api/v1/curriculum/module-3/units/fake",
            "backend.api.routes.curriculum.get_module_3_unit",
            True,
        ),
        (
            "/api/v1/curriculum/module-4/units/fake",
            "backend.api.routes.curriculum.get_module_4_unit",
            True,
        ),
        (
            "/api/v1/curriculum/module-5/units/fake",
            "backend.api.routes.curriculum.get_module_5_unit",
            True,
        ),
    ],
)
def test_unit_page_no_candidates_returns_500(
    client, monkeypatch, endpoint, getter, telemetry
):
    """Every get_*_unit_page raises 500 when no page passes max_complexity."""
    monkeypatch.setattr(getter, lambda _unit_id: _fake_unit(telemetry=telemetry))
    r = client.get(endpoint)
    assert r.status_code == 500
    assert "max_complexity" in r.json()["detail"]


def test_lesson_no_pages_returns_500(client, monkeypatch):
    """_build_lesson_payload raises 500 when the page list is empty."""
    monkeypatch.setattr(
        "backend.api.routes.curriculum.get_unit", lambda _unit_id: _fake_unit()
    )
    r = client.get("/api/v1/curriculum/units/fake/lesson")
    assert r.status_code == 500
    assert "no pages" in r.json()["detail"]


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/curriculum/module-2/units/nope/lesson",
        "/api/v1/curriculum/module-3/units/nope/lesson",
    ],
)
def test_lesson_unknown_unit_returns_404(client, endpoint):
    """Paid lesson endpoints return 404 for unknown units."""
    r = client.get(endpoint)
    assert r.status_code == 404


def test_next_unit_exits_loop_with_low_stability(client, monkeypatch):
    """Low stability walks every unit and covers the for-loop exit branch."""
    monkeypatch.setattr("backend.api.routes.curriculum._current_stability", lambda: 0.0)
    r = client.get("/api/v1/curriculum/next-unit")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "unit-8"


def test_module_2_next_breaks_and_defaults_to_first(client, monkeypatch):
    """High stability triggers the if-false break and chosen-is-None true branches."""
    monkeypatch.setattr("backend.api.routes.curriculum._current_stability", lambda: 0.8)
    r = client.get("/api/v1/curriculum/module-2/next")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "module2-unit-1"


def test_module_3_next_breaks_and_defaults_to_first(client, monkeypatch):
    monkeypatch.setattr("backend.api.routes.curriculum._current_stability", lambda: 0.7)
    r = client.get("/api/v1/curriculum/module-3/next")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "module3-unit-1"


def test_module_4_next_low_stability_exits_loop(client, monkeypatch):
    """Low stability covers the for-loop exit branch for module-4 next."""
    monkeypatch.setattr("backend.api.routes.curriculum._current_stability", lambda: 0.0)
    r = client.get("/api/v1/curriculum/module-4/next")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "module4-unit-6"


def test_module_4_next_high_stability_defaults_to_first(client, monkeypatch):
    """High stability covers the chosen-is-None true branch for module-4 next."""
    monkeypatch.setattr(
        "backend.api.routes.curriculum._current_stability", lambda: 0.75
    )
    r = client.get("/api/v1/curriculum/module-4/next")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "module4-unit-1"


def test_module_5_next_low_stability_exits_loop(client, monkeypatch):
    """Low stability covers for-exit, if-true, and chosen-not-None branches."""
    monkeypatch.setattr("backend.api.routes.curriculum._current_stability", lambda: 0.0)
    r = client.get("/api/v1/curriculum/module-5/next")
    assert r.status_code == 200
    assert r.json()["unit_id"] == "module5-unit-5"


def test_lesson_menu_org_visible_modules_none(client):
    """Authenticated learner with no org claim exercises _org_visible_modules None."""
    email = f"rack22-noorg-{uuid.uuid4()}@example.com"
    r = client.get("/api/v1/curriculum/menu", headers=_auth(email))
    assert r.status_code == 200
    module_ids = {m["id"] for m in r.json()["modules"]}
    assert 0 in module_ids
    assert 1 in module_ids


def test_lesson_menu_org_visible_modules_list(client):
    """Org with visible_modules set exercises the non-None list branch."""
    email = f"rack22-org-{uuid.uuid4()}@example.com"
    auth_user_id = uuid.uuid5(MOCK_NAMESPACE, email.lower())

    db = SessionLocal()
    try:
        account = Account(email=email, auth_user_id=auth_user_id)
        db.add(account)
        db.flush()

        product_code = f"rack22-prod-{uuid.uuid4()}"
        product = Product(
            code=product_code,
            display_name="Rack 2.2 product",
            price_cents=100,
            currency="usd",
            active=True,
            content_version=1,
        )
        purchase = Purchase(
            product_code=product_code,
            amount_cents=100,
            currency="usd",
            status="paid",
            buyer_account_id=account.id,
        )
        org = Organization(
            name="Rack Org",
            contact_email=email,
            admin_email=email,
            visible_modules=[2],
        )
        license_ = OrgLicense(
            organization=org,
            product_code=product_code,
            purchase=purchase,
            total_seats=1,
        )
        code = AccessCode(
            license=license_,
            code_hash=f"rack22-code-{uuid.uuid4()}",
            claimed_by_account_id=account.id,
            claimed_at=datetime.now(timezone.utc),
        )
        db.add_all([product, purchase, org, license_, code])
        db.commit()
    finally:
        db.close()

    r = client.get("/api/v1/curriculum/menu", headers=_auth(email))
    assert r.status_code == 200
    module_ids = [m["id"] for m in r.json()["modules"]]
    assert 0 in module_ids
    assert 1 in module_ids
    assert 2 in module_ids


def test_report_progress_branches(client):
    """Progress upsert covers all row/status/confidence branches."""
    unit_id = f"rack22-progress-unit-{uuid.uuid4()}"
    db = SessionLocal()
    try:
        db.add(
            Unit(id=unit_id, module_code="rack22", unit_index=0, title="Rack progress")
        )
        db.commit()
    finally:
        db.close()

    email = f"rack22-progress-{uuid.uuid4()}@example.com"
    client.headers.update(_auth(email))

    base = {"unit_id": unit_id}

    # New row, status started, confidence present.
    r = client.post(
        "/api/v1/curriculum/progress",
        json={**base, "status": "started", "confidence": 3},
    )
    assert r.status_code == 204

    # Existing row, status completed, confidence present.
    r = client.post(
        "/api/v1/curriculum/progress",
        json={**base, "status": "completed", "confidence": 5},
    )
    assert r.status_code == 204

    # Existing completed row, status completed, confidence absent.
    r = client.post(
        "/api/v1/curriculum/progress",
        json={**base, "status": "completed"},
    )
    assert r.status_code == 204

    # Existing completed row, status started, confidence absent.
    r = client.post(
        "/api/v1/curriculum/progress",
        json={**base, "status": "started"},
    )
    assert r.status_code == 204


def test_module_0_lesson_unknown_unit_returns_404(client):
    """Module 0 lesson endpoint returns 404 for an unknown unit."""
    r = client.get("/api/v1/curriculum/module-0/units/nope/lesson")
    assert r.status_code == 404


def test_org_visible_modules_branches(db_session):
    """Direct coverage for the _org_visible_modules helper branches."""
    email = f"rack22-org-direct-{uuid.uuid4()}@example.com"
    auth_user_id = uuid.uuid5(MOCK_NAMESPACE, email.lower())
    account = Account(email=email, auth_user_id=auth_user_id)
    db_session.add(account)
    db_session.flush()

    product_code = f"rack22-prod-{uuid.uuid4()}"
    product = Product(
        code=product_code,
        display_name="Rack product",
        price_cents=100,
        currency="usd",
        active=True,
        content_version=1,
    )
    purchase = Purchase(
        product_code=product_code,
        amount_cents=100,
        currency="usd",
        status="paid",
        buyer_account_id=account.id,
    )
    org = Organization(
        name="Rack Org",
        contact_email=email,
        admin_email=email,
        visible_modules=[2],
    )
    license_ = OrgLicense(
        organization=org,
        product_code=product_code,
        purchase=purchase,
        total_seats=1,
    )
    code = AccessCode(
        license=license_,
        code_hash=f"rack22-code-{uuid.uuid4()}",
        claimed_by_account_id=account.id,
        claimed_at=datetime.now(timezone.utc),
    )
    db_session.add_all([product, purchase, org, license_, code])
    db_session.flush()

    from backend.api.routes.curriculum import _org_visible_modules

    assert _org_visible_modules(db_session, account.id) == [2]

    other = Account(
        email=f"rack22-other-{uuid.uuid4()}@example.com",
        auth_user_id=uuid.uuid4(),
    )
    db_session.add(other)
    db_session.flush()
    assert _org_visible_modules(db_session, other.id) is None
