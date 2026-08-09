"""Account management routes.

EPIC-002 Phase 2: Account profile management endpoints.

Endpoints:
    PUT  /api/v1/account/profile    Update user profile (display name, preferences)
    GET  /api/v1/account/onboarding-status  Get onboarding progress
"""

from __future__ import annotations

import json
from typing import Optional, Any, Dict
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session as DbSession

from backend.api.deps import get_db
from backend.models.accounts import Account

# EPIC-002 Phase 2: New router for account management endpoints
account_profile_router = APIRouter()


# ---------------------------------------------------------------------------
# EPIC-002 Phase 2: Profile update endpoint
# ---------------------------------------------------------------------------


class ProfileUpdateRequest(BaseModel):
    """Request model for profile update."""

    displayName: str
    preferences: dict


class ProfileUpdateResponse(BaseModel):
    """Response model for profile update."""

    account_id: str
    display_name: str
    preferences: dict


@account_profile_router.put("/profile", response_model=ProfileUpdateResponse)
def update_profile(
    profile_data: ProfileUpdateRequest,
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> ProfileUpdateResponse:
    """Update user profile (display name and preferences).

    EPIC-002 Phase 2: This endpoint allows users to update their display name
    and learning preferences after account setup.

    Args:
        profile_data: Profile update data (display name, preferences)
        authorization: Bearer token header
        db: Database session

    Returns:
        Updated profile data

    Raises:
        401: Unauthorized (invalid or missing token)
        404: Account not found
    """
    # Token verification
    from backend.services.auth_verifier import parse_bearer, verify_token, AuthError

    token = parse_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "auth.no_credential", "message": "No credential provided"}},
        )

    try:
        claims = verify_token(token)
    except AuthError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": err.code, "message": err.message}},
        )

    if not claims.auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "auth.subject_missing", "message": "Subject missing"}},
        )

    # Get account
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .filter(Account.deleted_at.is_(None))
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "account.not_found", "message": "Account not found"}},
        )

    # Update profile
    account.display_name = profile_data.displayName.strip()
    # EPIC-002 Phase 2: Store preferences as JSON string
    account.preferences = json.dumps(profile_data.preferences) if profile_data.preferences else None

    db.commit()
    db.refresh(account)

    # Parse preferences back from JSON for response
    preferences_dict = {}
    if account.preferences:
        try:
            preferences_dict = json.loads(account.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences_dict = {}

    return ProfileUpdateResponse(
        account_id=str(account.id),
        display_name=account.display_name or "",
        preferences=preferences_dict,
    )


# ---------------------------------------------------------------------------
# EPIC-002 Phase 2: Onboarding status endpoint
# ---------------------------------------------------------------------------


class OnboardingStatusResponse(BaseModel):
    """Response model for onboarding status."""

    account_id: str
    onboarding_complete: bool
    display_name: Optional[str] = None
    preferences_set: bool = False


@account_profile_router.get("/onboarding-status", response_model=OnboardingStatusResponse)
def get_onboarding_status(
    authorization: Optional[str] = Header(default=None),
    db: DbSession = Depends(get_db),
) -> OnboardingStatusResponse:
    """Get onboarding progress for the current user.

    EPIC-002 Phase 2: This endpoint returns the onboarding status to determine
    if the user has completed account setup.

    Args:
        authorization: Bearer token header
        db: Database session

    Returns:
        Onboarding status data

    Raises:
        401: Unauthorized (invalid or missing token)
        404: Account not found
    """
    # Token verification
    from backend.services.auth_verifier import parse_bearer, verify_token, AuthError

    token = parse_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "auth.no_credential", "message": "No credential provided"}},
        )

    try:
        claims = verify_token(token)
    except AuthError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": err.code, "message": err.message}},
        )

    if not claims.auth_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "auth.subject_missing", "message": "Subject missing"}},
        )

    # Get account
    account = (
        db.query(Account)
        .filter(Account.auth_user_id == claims.auth_user_id)
        .filter(Account.deleted_at.is_(None))
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "account.not_found", "message": "Account not found"}},
        )

    # Determine onboarding status
    # EPIC-002 Phase 2: Parse preferences from JSON
    preferences_dict = {}
    if account.preferences:
        try:
            preferences_dict = json.loads(account.preferences)
        except (json.JSONDecodeError, TypeError):
            preferences_dict = {}

    onboarding_complete = bool(account.display_name and preferences_dict)
    preferences_set = bool(preferences_dict)

    return OnboardingStatusResponse(
        account_id=str(account.id),
        onboarding_complete=onboarding_complete,
        display_name=account.display_name,
        preferences_set=preferences_set,
    )