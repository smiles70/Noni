"""Rack 2.1 — targeted branch coverage for backend/services/organizations.py.

These are direct service tests using the rollback-isolated ``db_session``
fixture. They exercise the guard-negative and edge paths that route-level
happy-path tests leave uncovered, moving the module branch coverage toward
the intake 010 target (~66.8% combined backend branch coverage).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.config import settings
from backend.models.accounts import Account
from backend.models.billing import Product
from backend.models.learning import Progress, Unit
from backend.models.organizations import AccessCode, Organization
from backend.services import organizations as org_svc

PRODUCT_CODE = "rack21_product"


@pytest.fixture(scope="module", autouse=True)
def _seed_product_and_unit():
    """Persistent product + unit for the module; safe across full-suite runs."""
    engine = create_engine(settings.DATABASE_URL, future=True)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = Session()
    try:
        if db.query(Product).filter(Product.code == PRODUCT_CODE).one_or_none() is None:
            db.add(
                Product(
                    code=PRODUCT_CODE,
                    display_name="Rack21 product",
                    price_cents=100,
                    currency="usd",
                    active=True,
                    content_version=1,
                )
            )
            db.commit()
    finally:
        db.close()
        engine.dispose()
    yield


def _staff(db_session) -> Account:
    """Return a flushed staff account usable by service calls."""
    account = Account(
        auth_user_id=uuid.uuid4(),
        email=f"staff-{uuid.uuid4().hex[:8]}@example.test",
        staff_role="admin",
    )
    db_session.add(account)
    db_session.flush()
    return account


def _org(db_session, staff, **kwargs) -> Organization:
    """Create and commit an organization via the service."""
    defaults = {
        "name": f"Org {uuid.uuid4().hex[:8]}",
        "contact_email": "ops@example.test",
        "admin_email": "admin@example.test",
        "org_type": "nonprofit",
        "community_size": 10,
        "tier": "site",
        "custom_flag": False,
        "parent_org_id": None,
    }
    defaults.update(kwargs)
    return org_svc.create_organization(
        db_session,
        staff,
        **defaults,
    )


def _license(db_session, staff, org, *, total_seats: int = 10, **kwargs):
    """Create and commit a license via the service."""
    return org_svc.create_license(
        db_session,
        staff,
        org.id,
        product_code=PRODUCT_CODE,
        total_seats=total_seats,
        amount_cents=0,
        expires_at=kwargs.pop("expires_at", None),
        invoice_ref="rack21",
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Provisioning guards
# ---------------------------------------------------------------------------


def test_create_license_rejects_missing_product(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    with pytest.raises(HTTPException) as exc:
        org_svc.create_license(
            db_session,
            staff,
            org.id,
            product_code="no-such-product",
            total_seats=5,
            amount_cents=0,
            expires_at=None,
            invoice_ref="test",
        )
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail["envelope_id"] == "billing.product_unavailable"


def test_generate_codes_rejects_missing_license(db_session):
    with pytest.raises(HTTPException) as exc:
        org_svc.generate_codes(db_session, uuid.uuid4(), count=1)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail["envelope_id"] == "org.license_not_found"


def test_generate_codes_rejects_exceeding_seats(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=1)
    org_svc.generate_codes(db_session, lic.id, count=1)
    with pytest.raises(HTTPException) as exc:
        org_svc.generate_codes(db_session, lic.id, count=1)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail["envelope_id"] == "org.not_enough_seats"


def test_get_license_rejects_missing(db_session):
    with pytest.raises(HTTPException) as exc:
        org_svc._get_license(db_session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail["envelope_id"] == "org.license_not_found"


# ---------------------------------------------------------------------------
# License edits
# ---------------------------------------------------------------------------


def test_update_license_no_changes_is_no_op(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    updated = org_svc.update_license(db_session, staff, lic.id)
    assert updated.total_seats == 5
    assert updated.expires_at is None


def test_update_license_seats_only(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    updated = org_svc.update_license(db_session, staff, lic.id, total_seats=25)
    assert updated.total_seats == 25


def test_update_license_expires_only(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    expires = datetime(2030, 12, 31, tzinfo=timezone.utc)
    updated = org_svc.update_license(db_session, staff, lic.id, expires_at=expires)
    assert updated.expires_at == expires


def test_update_license_rejects_decrease_below_used(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    lic.used_seats = 3
    db_session.flush()
    with pytest.raises(HTTPException) as exc:
        org_svc.update_license(db_session, staff, lic.id, total_seats=1)
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail["envelope_id"] == "org.seat_below_used"


# ---------------------------------------------------------------------------
# License lifecycle idempotency
# ---------------------------------------------------------------------------


def test_suspend_license_is_idempotent(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    org_svc.suspend_license(db_session, staff, lic.id, reason="test")
    second = org_svc.suspend_license(db_session, staff, lic.id, reason="repeat")
    assert second.status == "suspended"


def test_reinstate_license_is_idempotent(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    first = org_svc.reinstate_license(db_session, staff, lic.id)
    assert first.status == "active"


# ---------------------------------------------------------------------------
# Org lifecycle
# ---------------------------------------------------------------------------


def test_org_or_404_rejects_missing(db_session):
    with pytest.raises(HTTPException) as exc:
        org_svc._org_or_404(db_session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail["envelope_id"] == "org.org_not_found"


def test_suspend_org_can_include_children(db_session):
    staff = _staff(db_session)
    parent = _org(db_session, staff, name="Parent Rack21")
    child = _org(
        db_session,
        staff,
        name="Child Rack21",
        parent_org_id=parent.id,
    )
    org_svc.suspend_org(
        db_session,
        staff,
        parent.id,
        reason="test",
        include_children=True,
    )
    assert parent.status == "suspended"
    assert child.status == "suspended"


def test_reinstate_org_skips_active_children_and_reinstates_suspended(db_session):
    staff = _staff(db_session)
    parent = _org(db_session, staff, name="Parent Rack21")
    active_child = _org(
        db_session,
        staff,
        name="Active Child",
        parent_org_id=parent.id,
    )
    suspended_child = _org(
        db_session,
        staff,
        name="Suspended Child",
        parent_org_id=parent.id,
    )
    suspended_child.status = "suspended"
    db_session.flush()

    org_svc.reinstate_org(
        db_session,
        staff,
        parent.id,
        include_children=True,
    )
    assert active_child.status == "active"
    assert suspended_child.status == "active"


# ---------------------------------------------------------------------------
# Usage
# ---------------------------------------------------------------------------


def test_org_usage_no_licenses_raises(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    with pytest.raises(HTTPException) as exc:
        org_svc.org_usage(db_session, org.id)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_org_usage_returns_first_license(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=3)
    org_svc.generate_codes(db_session, lic.id, count=2)
    usage = org_svc.org_usage(db_session, org.id)
    assert usage["total_seats"] == 3
    assert len(usage["codes"]) == 2


# ---------------------------------------------------------------------------
# Redemption guards
# ---------------------------------------------------------------------------


def _redeemer(db_session) -> Account:
    account = Account(
        auth_user_id=uuid.uuid4(),
        email=f"redeemer-{uuid.uuid4().hex[:8]}@example.test",
    )
    db_session.add(account)
    db_session.flush()
    return account


def test_redeem_code_idempotent_for_same_account(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    account = _redeemer(db_session)
    first = org_svc.redeem_code(db_session, account, codes[0])
    assert first["granted"] is True
    second = org_svc.redeem_code(db_session, account, codes[0])
    assert second["granted"] is True


def test_redeem_code_rejects_already_claimed_by_other_account(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    owner = _redeemer(db_session)
    org_svc.redeem_code(db_session, owner, codes[0])
    other = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, other, codes[0])
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail["envelope_id"] == "org.code_already_claimed"


def test_redeem_code_rejects_expired_license(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    expired = datetime(2000, 1, 1, tzinfo=timezone.utc)
    lic = _license(db_session, staff, org, total_seats=5, expires_at=expired)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    account = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, account, codes[0])
    assert exc.value.status_code == status.HTTP_410_GONE
    assert exc.value.detail["envelope_id"] == "org.license_expired"


def test_redeem_code_rejects_full_license(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=1)
    lic.used_seats = lic.total_seats
    db_session.flush()
    code = org_svc.generate_code_token()
    db_session.add(AccessCode(license_id=lic.id, code_hash=org_svc.hash_code(code)))
    db_session.flush()
    account = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, account, code)
    assert exc.value.status_code == status.HTTP_410_GONE
    assert exc.value.detail["envelope_id"] == "org.license_full"


# ---------------------------------------------------------------------------
# Engagement aggregates
# ---------------------------------------------------------------------------


def test_license_engagement_below_k_anonymity_floor(db_session):
    codes = [AccessCode(claimed_by_account_id=uuid.uuid4()) for _ in range(2)]
    result = org_svc.license_engagement(db_session, codes)
    assert result["cohort"] == 2
    assert result["min_cohort_met"] is False


def test_license_engagement_meets_k_anonymity_floor(db_session):
    codes = [AccessCode(claimed_by_account_id=uuid.uuid4()) for _ in range(5)]
    result = org_svc.license_engagement(db_session, codes)
    assert result["cohort"] == 5
    assert result["min_cohort_met"] is True
    assert "units_completed" in result


def test_org_engagement_below_k_anonymity_floor(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=3)
    account = _redeemer(db_session)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    org_svc.redeem_code(db_session, account, codes[0])
    result = org_svc.org_engagement(db_session, org.id)
    assert result["cohort"] == 1
    assert result["min_cohort_met"] is False


def _engagement_unit(db_session) -> str:
    unit_id = f"rack21-unit-{uuid.uuid4().hex[:8]}"
    db_session.add(
        Unit(
            id=unit_id,
            module_code="module0",
            unit_index=1,
            title="Rack21 unit",
        )
    )
    db_session.flush()
    return unit_id


def test_org_engagement_meets_k_anonymity_floor_with_progress(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=10)
    codes = org_svc.generate_codes(db_session, lic.id, count=5)
    unit_id = _engagement_unit(db_session)
    now = datetime.now(timezone.utc)
    accounts = []
    for token in codes:
        account = _redeemer(db_session)
        accounts.append(account)
        org_svc.redeem_code(db_session, account, token)
        db_session.add(
            Progress(
                account_id=account.id,
                unit_id=unit_id,
                status="completed",
                first_started_at=now,
                completed_at=now,
                confidence_pre=2,
                confidence_post=4,
            )
        )
    db_session.flush()
    result = org_svc.org_engagement(db_session, org.id)
    assert result["cohort"] == 5
    assert result["min_cohort_met"] is True
    assert result["units_completed"] == 5
    assert result["active_last_7d"] == 5
    assert result["avg_confidence_delta"] == 2.0
    assert result["learners_started"] == 5


# ---------------------------------------------------------------------------
# Public + staff slug surfaces
# ---------------------------------------------------------------------------


def test_org_public_page_found_and_not_found(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    slug = f"rack21-{uuid.uuid4().hex[:8]}"
    org_svc.set_org_slug(db_session, org.id, slug)
    page = org_svc.org_public_page(db_session, slug)
    assert page["name"] == org.name

    with pytest.raises(HTTPException) as exc:
        org_svc.org_public_page(db_session, "no-such-slug")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_set_org_slug_branches(db_session):
    staff = _staff(db_session)
    org_a = _org(db_session, staff, name="Org A Rack21")
    slug = f"rack21-slug-{uuid.uuid4().hex[:8]}"

    first = org_svc.set_org_slug(db_session, org_a.id, slug)
    assert first["changed"] is True

    same = org_svc.set_org_slug(db_session, org_a.id, slug)
    assert same["changed"] is False

    org_b = _org(db_session, staff, name="Org B Rack21")
    with pytest.raises(HTTPException) as exc:
        org_svc.set_org_slug(db_session, org_b.id, slug)
    assert exc.value.status_code == status.HTTP_409_CONFLICT
    assert exc.value.detail["envelope_id"] == "org.slug_taken"

    with pytest.raises(HTTPException) as exc:
        org_svc.set_org_slug(db_session, uuid.uuid4(), "unused")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Dashboard, search, detail
# ---------------------------------------------------------------------------


def test_org_dashboard_missing_org(db_session):
    with pytest.raises(HTTPException) as exc:
        org_svc.org_dashboard(db_session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_org_dashboard_with_and_without_licenses(db_session):
    staff = _staff(db_session)
    empty_org = _org(db_session, staff, name="Empty Rack21")
    empty = org_svc.org_dashboard(db_session, empty_org.id)
    assert empty["licenses"] == []

    org = _org(db_session, staff, name="Dashboard Rack21")
    expires = datetime.now(timezone.utc) + timedelta(days=7)
    lic = _license(db_session, staff, org, total_seats=2, expires_at=expires)
    org_svc.generate_codes(db_session, lic.id, count=1)
    dash = org_svc.org_dashboard(db_session, org.id)
    assert len(dash["licenses"]) == 1
    assert dash["licenses"][0]["expiring_soon"] is True


def test_org_search_blank_and_query(db_session):
    staff = _staff(db_session)
    name = f"Searchable Rack21 {uuid.uuid4().hex[:8]}"
    org = _org(db_session, staff, name=name)

    recent = org_svc.org_search(db_session, "")
    assert any(o["id"] == str(org.id) for o in recent)

    found = org_svc.org_search(db_session, name.split()[1].lower())
    assert any(o["id"] == str(org.id) for o in found)


def test_org_detail_missing_org(db_session):
    with pytest.raises(HTTPException) as exc:
        org_svc.org_detail(db_session, uuid.uuid4())
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_org_detail_returns_existing_org(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff, name="Detail Rack21")
    detail = org_svc.org_detail(db_session, org.id)
    assert detail["org"]["id"] == str(org.id)
    assert "licenses" in detail
    assert "audit" in detail


# ---------------------------------------------------------------------------
# Remaining branch fills discovered after first coverage run
# ---------------------------------------------------------------------------


def test_create_organization_with_contacts(db_session):
    staff = _staff(db_session)
    org = _org(
        db_session,
        staff,
        name="Contacts Rack21",
        contacts=[
            {"name": "Pat", "email": "pat@example.test", "is_primary": True},
            {"name": "Sam", "email": "sam@example.test", "is_primary": True},
        ],
    )
    assert len(org.contacts) == 2
    assert sum(1 for c in org.contacts if c.is_primary) == 1


def test_generate_codes_rejects_suspended_org(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    org_svc.suspend_org(db_session, staff, org.id, reason="test")
    with pytest.raises(HTTPException) as exc:
        org_svc.generate_codes(db_session, lic.id, count=1)
    assert exc.value.status_code == status.HTTP_410_GONE
    assert exc.value.detail["envelope_id"] == "org.org_suspended"


def test_reinstate_license_restores_suspended(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    org_svc.suspend_license(db_session, staff, lic.id, reason="test")
    restored = org_svc.reinstate_license(db_session, staff, lic.id)
    assert restored.status == "active"
    assert restored.suspension_reason is None


def test_redeem_code_rejects_missing_code(db_session):
    account = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, account, "no-such-code")
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail["envelope_id"] == "org.code_not_found"


def test_redeem_code_rejects_suspended_license(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    org_svc.suspend_license(db_session, staff, lic.id, reason="test")
    account = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, account, codes[0])
    assert exc.value.status_code == status.HTTP_410_GONE
    assert exc.value.detail["envelope_id"] == "org.license_suspended"


def test_redeem_code_rejects_suspended_org(db_session):
    staff = _staff(db_session)
    org = _org(db_session, staff)
    lic = _license(db_session, staff, org, total_seats=5)
    codes = org_svc.generate_codes(db_session, lic.id, count=1)
    org_svc.suspend_org(db_session, staff, org.id, reason="test")
    account = _redeemer(db_session)
    with pytest.raises(HTTPException) as exc:
        org_svc.redeem_code(db_session, account, codes[0])
    assert exc.value.status_code == status.HTTP_410_GONE
    assert exc.value.detail["envelope_id"] == "org.org_suspended"


def test_suspend_org_without_children(db_session):
    staff = _staff(db_session)
    parent = _org(db_session, staff, name="Parent No Children")
    child = _org(
        db_session,
        staff,
        name="Child Should Stay Active",
        parent_org_id=parent.id,
    )
    org_svc.suspend_org(db_session, staff, parent.id, reason="test")
    assert parent.status == "suspended"
    assert child.status == "active"


def test_suspend_org_skips_already_suspended_child(db_session):
    staff = _staff(db_session)
    parent = _org(db_session, staff, name="Parent Skip Child")
    child = _org(
        db_session,
        staff,
        name="Already Suspended Child",
        parent_org_id=parent.id,
    )
    child.status = "suspended"
    db_session.flush()
    org_svc.suspend_org(
        db_session, staff, parent.id, reason="test", include_children=True
    )
    assert parent.status == "suspended"
    assert child.status == "suspended"


def test_reinstate_org_without_children(db_session):
    staff = _staff(db_session)
    parent = _org(db_session, staff, name="Parent Reinstate No Children")
    child = _org(
        db_session,
        staff,
        name="Child Should Stay Active",
        parent_org_id=parent.id,
    )
    parent.status = "suspended"
    db_session.flush()
    org_svc.reinstate_org(db_session, staff, parent.id, include_children=False)
    assert parent.status == "active"
    assert child.status == "active"
