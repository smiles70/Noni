"""Authentication routes.

See ADR 0023 (original session-cookie design) and ADR 0024 (Clerk
migration; this module's current shape).

Endpoints:
- GET /auth/whoami   return current account or 401

Removed in ADR 0024:
- POST /auth/callback  (no session table to populate; Bearer tokens
                        are verified per-request by `get_current_account`)
- POST /auth/signout   (sign-out is client-side: `clerk.signOut()` in
                        Clerk mode, localStorage clear in mock mode;
                        tokens we issued expire on their own)

The `credential` exchange endpoint and the `sessions` table outlived
their usefulness once we standardised on Clerk + per-request JWT
verification. Removing them eliminates the cross-origin cookie /
SameSite / CSRF surface that caused repeated sign-in loops during the
migration.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.api.deps import get_current_account
from backend.models.accounts import Account


router = APIRouter()


class WhoAmIResponse(BaseModel):
    """Shape returned by /auth/whoami.

    `has_active_session` is preserved as the frontend's compatibility
    field — in the Bearer model a successful response by definition
    means "active". A 401 (no/invalid token) returns no body, and the
    frontend treats that as signed-out.
    """

    account_id: str
    # Email may be missing in pathological provider states (e.g. an
    # account row predating the Clerk migration). Treat as nullable on
    # the wire so we don't 500 instead of returning a usable response.
    email: Optional[str] = None
    display_name: Optional[str] = None
    has_active_session: bool = True


@router.get("/whoami", response_model=WhoAmIResponse)
def auth_whoami(
    account: Account = Depends(get_current_account),
) -> WhoAmIResponse:
    return WhoAmIResponse(
        account_id=str(account.id),
        email=account.email,
        display_name=account.display_name,
        has_active_session=True,
    )
