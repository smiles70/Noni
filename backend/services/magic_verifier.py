"""Magic.link DID token verification.

Uses the `magic-admin` Python SDK to validate the cryptographic proof in a
Decentralized ID (DID) token and to fetch user metadata for account
materialization. See ADR 0027 and `.ai/process/MAGIC_IMPLEMENTATION_RESEARCH.md`.

The `Magic` client is initialised lazily; a missing or invalid secret key is
treated as a transient verifier failure and causes the application to fail
closed (B5, B11).
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from magic_admin import Magic
from magic_admin.error import (
    DIDTokenExpired,
    DIDTokenInvalid,
    DIDTokenMalformed,
    MagicError,
)

from backend.core.config import settings

logger = logging.getLogger("noni.magic")

MAGIC_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000002")

_magic_client: Optional[Magic] = None
_magic_client_error: bool = False


def _get_magic_client() -> Optional[Magic]:
    """Return a cached Magic Admin client; return None on setup failure."""
    global _magic_client, _magic_client_error

    if _magic_client is not None:
        return _magic_client
    if _magic_client_error:
        return None

    secret = settings.MAGIC_API_SECRET_KEY.strip()
    client_id = settings.MAGIC_CLIENT_ID.strip() or None

    if not secret:
        logger.error("magic_setup_missing_secret")
        _magic_client_error = True
        return None

    try:
        _magic_client = Magic(api_secret_key=secret, client_id=client_id)
        return _magic_client
    except MagicError as exc:
        logger.error("magic_setup_failed: %s", exc.__class__.__name__)
        _magic_client_error = True
        return None
    except Exception:
        logger.exception("magic_setup_unexpected")
        _magic_client_error = True
        return None


def reset_magic_client() -> None:
    """Reset the cached client; useful for tests and config reload."""
    global _magic_client, _magic_client_error
    _magic_client = None
    _magic_client_error = False


def _sub_to_auth_user_id(sub: str) -> uuid.UUID:
    """Stable UUID derived from the Magic `sub` (issuer/user) claim."""
    return uuid.uuid5(MAGIC_NAMESPACE, sub)


def validate_did_token(did_token: str) -> Optional[dict]:
    """Validate a DID token and return its claims dict, or None if invalid.

    The returned dict contains at least `sub`, `iss`, `iat`, `ext`, `nbf`,
    `aud`, and `tid`. Email is not present in the DID token; use
    `fetch_user_profile_by_token` for the email.
    """
    client = _get_magic_client()
    if client is None:
        return None

    try:
        client.Token.validate(did_token)
    except DIDTokenExpired:
        logger.info("magic_did_expired")
        return None
    except DIDTokenMalformed:
        logger.info("magic_did_malformed")
        return None
    except DIDTokenInvalid:
        logger.info("magic_did_invalid")
        return None
    except MagicError as exc:
        logger.warning("magic_validation_error: %s", exc.__class__.__name__)
        return None
    except Exception:
        logger.exception("magic_validation_unexpected")
        return None

    try:
        _proof, claim = client.Token.decode(did_token)
    except DIDTokenMalformed:
        logger.info("magic_did_decode_malformed")
        return None
    except Exception:
        logger.exception("magic_did_decode_unexpected")
        return None

    sub = claim.get("sub")
    if not sub:
        logger.info("magic_did_missing_sub")
        return None

    return dict(claim)


def fetch_user_profile_by_token(did_token: str) -> Optional[dict]:
    """Fetch user metadata (email, etc.) from the Magic API for a DID token.

    This is a network call and is intended only for first-time account
    materialisation (`/auth/session/init`), not for every request.
    """
    client = _get_magic_client()
    if client is None:
        return None

    try:
        resp = client.User.get_metadata_by_token(did_token)
    except MagicError as exc:
        logger.warning("magic_user_metadata_error: %s", exc.__class__.__name__)
        return None
    except Exception:
        logger.exception("magic_user_metadata_unexpected")
        return None

    data = getattr(resp, "data", resp)
    if not isinstance(data, dict):
        return None
    return data
