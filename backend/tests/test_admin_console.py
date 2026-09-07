"""AC-1: admin console access control.

The console is staff-only by design — same guard family as the org
dashboard tests. whoami-check is the soft probe for the frontend gate.
"""

from __future__ import annotations

import uuid


def test_whoami_requires_session(client):
    r = client.get("/api/v1/admin/whoami")
    assert r.status_code == 401
    assert r.json()["detail"]["envelope_id"] == "auth.signed_out"


def test_whoami_check_is_soft(client):
    r = client.get("/api/v1/admin/whoami-check")
    assert r.status_code == 200
    assert r.json() == {"staff": False}


def test_orgs_rejects_non_staff(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/orgs?q=oak")
    assert r.status_code == 403


def test_orgs_requires_min_query(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/orgs?q=ab")
    assert r.status_code in (403, 422)


def test_flags_rejects_non_staff(authenticated_client):
    r = authenticated_client.get("/api/v1/admin/flags")
    assert r.status_code == 403
