"""Sprint B2: Supabase JWT verification.

Covers the failure modes that matter to a fail-closed identity boundary:

  - valid token                -> AuthClaims with sub/email/display_name
  - expired token              -> None
  - wrong audience             -> None
  - wrong issuer               -> None
  - tampered signature         -> None
  - missing required claim     -> None
  - malformed sub (not a UUID) -> None
  - missing/garbled email      -> None
  - empty / non-string input   -> None
  - provider rejects empty secret at construction time

Every rejection path is asserted to return None (not raise) so the
auth route surfaces the same `auth.signed_out` envelope regardless of
the specific failure — no enumeration oracle for attackers.
"""

from __future__ import annotations

import time
import uuid
from typing import Optional

import jwt
import pytest

from backend.services.auth_provider import SupabaseAuthProvider

SECRET = "test-secret-for-unit-tests-only"
AUD = "authenticated"
ISS = "https://example.supabase.co/auth/v1"


def _sign(
    payload: dict,
    *,
    secret: str = SECRET,
    algorithm: str = "HS256",
) -> str:
    return jwt.encode(payload, secret, algorithm=algorithm)


def _base_payload(
    *,
    sub: Optional[str] = None,
    email: str = "alice@example.test",
    aud: str = AUD,
    iss: str = ISS,
    exp_offset: int = 60,
    extra: Optional[dict] = None,
) -> dict:
    now = int(time.time())
    payload = {
        "sub": sub or str(uuid.uuid4()),
        "email": email,
        "aud": aud,
        "iss": iss,
        "iat": now,
        "exp": now + exp_offset,
    }
    if extra:
        payload.update(extra)
    return payload


def _provider() -> SupabaseAuthProvider:
    return SupabaseAuthProvider(jwt_secret=SECRET, audience=AUD, issuer=ISS)


def test_valid_token_returns_claims():
    sub = str(uuid.uuid4())
    token = _sign(
        _base_payload(
            sub=sub,
            email="Alice@Example.Test",
            extra={"user_metadata": {"full_name": "Alice Example"}},
        )
    )
    claims = _provider().verify_credential(token)
    assert claims is not None
    assert claims.auth_user_id == uuid.UUID(sub)
    # Email is normalised to lowercase.
    assert claims.email == "alice@example.test"
    assert claims.display_name == "Alice Example"


def test_valid_token_without_user_metadata_has_no_display_name():
    token = _sign(_base_payload())
    claims = _provider().verify_credential(token)
    assert claims is not None
    assert claims.display_name is None


def test_expired_token_is_rejected():
    token = _sign(_base_payload(exp_offset=-10))
    assert _provider().verify_credential(token) is None


def test_wrong_audience_is_rejected():
    token = _sign(_base_payload(aud="anon"))
    assert _provider().verify_credential(token) is None


def test_wrong_issuer_is_rejected():
    token = _sign(_base_payload(iss="https://evil.example.com/auth/v1"))
    assert _provider().verify_credential(token) is None


def test_tampered_signature_is_rejected():
    token = _sign(_base_payload())
    # Flip a byte in the signature.
    head, payload, sig = token.split(".")
    tampered = ".".join(
        [head, payload, sig[:-2] + ("AA" if sig[-2:] != "AA" else "BB")]
    )
    assert _provider().verify_credential(tampered) is None


def test_token_signed_with_wrong_secret_is_rejected():
    token = _sign(_base_payload(), secret="not-the-real-secret")
    assert _provider().verify_credential(token) is None


def test_missing_exp_is_rejected():
    payload = _base_payload()
    payload.pop("exp")
    token = _sign(payload)
    assert _provider().verify_credential(token) is None


def test_missing_sub_is_rejected():
    payload = _base_payload()
    payload.pop("sub")
    token = _sign(payload)
    assert _provider().verify_credential(token) is None


def test_non_uuid_sub_is_rejected():
    token = _sign(_base_payload(sub="not-a-uuid"))
    assert _provider().verify_credential(token) is None


def test_missing_email_is_rejected():
    payload = _base_payload()
    payload.pop("email")
    token = _sign(payload)
    assert _provider().verify_credential(token) is None


def test_garbled_email_is_rejected():
    token = _sign(_base_payload(email="not-an-email"))
    assert _provider().verify_credential(token) is None


def test_empty_credential_is_rejected():
    assert _provider().verify_credential("") is None


def test_non_string_credential_is_rejected():
    # type: ignore[arg-type] — we want to assert defensive runtime behavior.
    assert _provider().verify_credential(None) is None  # type: ignore[arg-type]
    assert _provider().verify_credential(12345) is None  # type: ignore[arg-type]


def test_garbage_credential_is_rejected():
    assert _provider().verify_credential("not.a.jwt") is None


def test_provider_rejects_empty_secret_at_construction():
    with pytest.raises(ValueError, match="non-empty JWT secret"):
        SupabaseAuthProvider(jwt_secret="")


def test_issuer_check_is_skipped_when_unset():
    """Backwards compat: if issuer is left blank, any iss is accepted."""
    provider = SupabaseAuthProvider(jwt_secret=SECRET, audience=AUD, issuer=None)
    token = _sign(_base_payload(iss="https://anywhere.example.com"))
    assert provider.verify_credential(token) is not None
