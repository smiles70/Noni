"""Rack 2.13: Magic.link DID token verifier branch coverage."""

from __future__ import annotations

import pytest

from backend.core.config import settings
from backend.services import magic_verifier as mv


class FakeMagicError(Exception):
    pass


class FakeDIDTokenExpired(Exception):
    pass


class FakeDIDTokenInvalid(Exception):
    pass


class FakeDIDTokenMalformed(Exception):
    pass


class FakeMagic:
    def __init__(self, *, api_secret_key, client_id=None):
        self.api_secret_key = api_secret_key
        self.client_id = client_id
        self.validate_called = False
        self.decode_called = False
        self.get_metadata_called = False
        self.validate_raise = None
        self.decode_raise = None
        self.decode_claim = {}
        self.get_metadata_return = None

    class Token:
        @staticmethod
        def validate(did_token):
            # The validate method is called on the class via the instance.
            pass

        @staticmethod
        def decode(did_token):
            return None, {}

    class User:
        @staticmethod
        def get_metadata_by_token(did_token):
            return None


@pytest.fixture(autouse=True)
def _reset_magic_client():
    mv.reset_magic_client()
    yield
    mv.reset_magic_client()


@pytest.fixture
def patched(monkeypatch):
    """Patch Magic and error classes in the magic_verifier module."""
    monkeypatch.setattr(mv, "Magic", FakeMagic)
    monkeypatch.setattr(mv, "MagicError", FakeMagicError)
    monkeypatch.setattr(mv, "DIDTokenExpired", FakeDIDTokenExpired)
    monkeypatch.setattr(mv, "DIDTokenInvalid", FakeDIDTokenInvalid)
    monkeypatch.setattr(mv, "DIDTokenMalformed", FakeDIDTokenMalformed)
    monkeypatch.setattr(settings, "MAGIC_API_SECRET_KEY", "sk_test_123")
    monkeypatch.setattr(settings, "MAGIC_CLIENT_ID", "")


# ---------------------------------------------------------------------------
# _get_magic_client
# ---------------------------------------------------------------------------


def test_get_magic_client_returns_cached_instance(patched):
    first = mv._get_magic_client()
    second = mv._get_magic_client()
    assert first is second


def test_get_magic_client_returns_none_when_previous_error(patched):
    mv._magic_client_error = True
    assert mv._get_magic_client() is None


def test_get_magic_client_returns_none_when_secret_missing(patched, monkeypatch):
    monkeypatch.setattr(settings, "MAGIC_API_SECRET_KEY", "")
    assert mv._get_magic_client() is None
    assert mv._magic_client_error is True


def test_get_magic_client_returns_none_on_magic_error(patched, monkeypatch):
    class _BoomMagic(FakeMagic):
        def __init__(self, *, api_secret_key, client_id=None):
            raise FakeMagicError("setup failed")

    monkeypatch.setattr(mv, "Magic", _BoomMagic)
    assert mv._get_magic_client() is None
    assert mv._magic_client_error is True


def test_get_magic_client_returns_none_on_unexpected_error(patched, monkeypatch):
    class _BoomMagic(FakeMagic):
        def __init__(self, *, api_secret_key, client_id=None):
            raise RuntimeError("boom")

    monkeypatch.setattr(mv, "Magic", _BoomMagic)
    assert mv._get_magic_client() is None
    assert mv._magic_client_error is True


# ---------------------------------------------------------------------------
# validate_did_token
# ---------------------------------------------------------------------------


def _make_client(
    *,
    validate_raise=None,
    decode_raise=None,
    decode_claim=None,
):
    client = FakeMagic(api_secret_key="sk", client_id=None)

    def _validate(did_token):
        if validate_raise:
            raise validate_raise()

    def _decode(did_token):
        if decode_raise:
            raise decode_raise()
        return None, decode_claim or {}

    client.Token.validate = staticmethod(_validate)
    client.Token.decode = staticmethod(_decode)
    return client


def test_validate_did_token_returns_none_when_client_none():
    mv._magic_client_error = True
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_expired(monkeypatch, patched):
    client = _make_client(validate_raise=FakeDIDTokenExpired)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_malformed_validate(monkeypatch, patched):
    client = _make_client(validate_raise=FakeDIDTokenMalformed)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_invalid(monkeypatch, patched):
    client = _make_client(validate_raise=FakeDIDTokenInvalid)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_magic_error(monkeypatch, patched):
    client = _make_client(validate_raise=FakeMagicError)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_unexpected_validate_error(
    monkeypatch, patched
):
    client = _make_client(validate_raise=RuntimeError)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_malformed_decode(monkeypatch, patched):
    client = _make_client(decode_raise=FakeDIDTokenMalformed)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_on_unexpected_decode_error(
    monkeypatch, patched
):
    client = _make_client(decode_raise=RuntimeError)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_none_when_sub_missing(monkeypatch, patched):
    client = _make_client(decode_claim={"iss": "did:magic"})
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.validate_did_token("token") is None


def test_validate_did_token_returns_claims_on_success(monkeypatch, patched):
    claim = {"sub": "did:magic:123"}
    client = _make_client(decode_claim=claim)
    monkeypatch.setattr(mv, "_magic_client", client)
    result = mv.validate_did_token("token")
    assert result == claim


# ---------------------------------------------------------------------------
# fetch_user_profile_by_token
# ---------------------------------------------------------------------------


def _make_user_client(*, metadata=None, raise_on_call=None):
    client = FakeMagic(api_secret_key="sk", client_id=None)

    def _get_metadata(did_token):
        if raise_on_call:
            raise raise_on_call()
        return _Response(metadata)

    client.User.get_metadata_by_token = staticmethod(_get_metadata)
    return client


class _Response:
    def __init__(self, data):
        self.data = data


def test_fetch_user_profile_returns_none_when_client_none():
    mv._magic_client_error = True
    assert mv.fetch_user_profile_by_token("token") is None


def test_fetch_user_profile_returns_none_on_magic_error(monkeypatch, patched):
    client = _make_user_client(raise_on_call=FakeMagicError)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.fetch_user_profile_by_token("token") is None


def test_fetch_user_profile_returns_none_on_unexpected_error(monkeypatch, patched):
    client = _make_user_client(raise_on_call=RuntimeError)
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.fetch_user_profile_by_token("token") is None


def test_fetch_user_profile_returns_none_when_data_not_dict(monkeypatch, patched):
    client = _make_user_client(metadata="not-a-dict")
    monkeypatch.setattr(mv, "_magic_client", client)
    assert mv.fetch_user_profile_by_token("token") is None


def test_fetch_user_profile_returns_data_when_dict(monkeypatch, patched):
    client = _make_user_client(metadata={"email": "test@example.com"})
    monkeypatch.setattr(mv, "_magic_client", client)
    result = mv.fetch_user_profile_by_token("token")
    assert result == {"email": "test@example.com"}
