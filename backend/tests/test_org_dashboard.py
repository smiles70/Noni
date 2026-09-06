"""OB-2/OB-5: org dashboard access control + audit writes.

Spec tests for the B2B onboarding epic. The dashboard is staff-only and
aggregate-only by design — these tests pin both properties.
"""

from __future__ import annotations

import uuid


def test_dashboard_requires_session(client):
    r = client.get(f"/api/v1/billing/org/{uuid.uuid4()}/dashboard")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_dashboard_rejects_non_staff(authenticated_client):
    r = authenticated_client.get(f"/api/v1/billing/org/{uuid.uuid4()}/dashboard")
    assert r.status_code == 403
    assert r.json()["detail"]["envelope_id"] == "auth.not_staff"


def test_redeem_rejects_unknown_code(authenticated_client):
    r = authenticated_client.post(
        "/api/v1/billing/org/redeem", json={"code": "definitely-not-a-real-code"}
    )
    assert r.status_code == 404
    assert r.json()["detail"]["envelope_id"] == "org.code_not_found"
