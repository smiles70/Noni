"""Tests for the Magic.link DID verifier and provider."""

from unittest.mock import MagicMock

import pytest

from backend.services.auth_provider import AuthClaims, MagicAuthProvider
from backend.services.magic_verifier import (
    fetch_user_profile_by_token,
    reset_magic_client,
    validate_did_token,
)


@pytest.fixture(autouse=True)
def reset_client():
    reset_magic_client()
    yield
    reset_magic_client()


@pytest.fixture
def mock_client(monkeypatch):
    client = MagicMock()
    client.Token = MagicMock()
    client.User = MagicMock()
    # Prevent real network: stub the client factory.
    monkeypatch.setattr(
        "backend.services.magic_verifier._get_magic_client",
        lambda: client,
    )
    return client


class TestValidateDidToken:
    def test_valid_token_returns_claim(self, mock_client):
        mock_client.Token.validate.return_value = None
        mock_client.Token.decode.return_value = ("proof", {"sub": "did:ethr:abc"})

        claim = validate_did_token("fake.did.token")

        assert claim == {"sub": "did:ethr:abc"}
        mock_client.Token.validate.assert_called_once_with("fake.did.token")
        mock_client.Token.decode.assert_called_once_with("fake.did.token")

    def test_expired_token_returns_none(self, mock_client):
        from magic_admin.error import DIDTokenExpired

        mock_client.Token.validate.side_effect = DIDTokenExpired("expired")
        assert validate_did_token("fake.did.token") is None

    def test_invalid_token_returns_none(self, mock_client):
        from magic_admin.error import DIDTokenInvalid

        mock_client.Token.validate.side_effect = DIDTokenInvalid("invalid")
        assert validate_did_token("fake.did.token") is None

    def test_malformed_token_returns_none(self, mock_client):
        from magic_admin.error import DIDTokenMalformed

        mock_client.Token.validate.side_effect = DIDTokenMalformed("malformed")
        assert validate_did_token("fake.did.token") is None

    def test_missing_sub_returns_none(self, mock_client):
        mock_client.Token.validate.return_value = None
        mock_client.Token.decode.return_value = ("proof", {"iss": "issuer"})
        assert validate_did_token("fake.did.token") is None

    def test_setup_failure_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            "backend.services.magic_verifier._get_magic_client", lambda: None
        )
        assert validate_did_token("fake.did.token") is None


class TestFetchUserProfile:
    def test_profile_returned(self, mock_client):
        response = MagicMock()
        response.data = {"email": "learner@example.com", "display_name": "Learner"}
        mock_client.User.get_metadata_by_token.return_value = response

        data = fetch_user_profile_by_token("fake.did.token")

        assert data == {"email": "learner@example.com", "display_name": "Learner"}

    def test_error_returns_none(self, mock_client):
        from magic_admin.error import MagicError

        mock_client.User.get_metadata_by_token.side_effect = MagicError("boom")
        assert fetch_user_profile_by_token("fake.did.token") is None


class TestMagicAuthProvider:
    def test_verify_credential(self, mock_client):
        mock_client.Token.validate.return_value = None
        mock_client.Token.decode.return_value = ("proof", {"sub": "did:ethr:abc"})

        provider = MagicAuthProvider()
        claims = provider.verify_credential("fake.did.token")

        assert isinstance(claims, AuthClaims)
        assert claims.subject == "did:ethr:abc"
        assert claims.email is None

    def test_verify_credential_invalid_returns_none(self, mock_client):
        from magic_admin.error import DIDTokenInvalid

        mock_client.Token.validate.side_effect = DIDTokenInvalid("bad")

        provider = MagicAuthProvider()
        assert provider.verify_credential("fake.did.token") is None

    def test_fetch_user_profile(self, mock_client):
        response = MagicMock()
        response.data = {"email": "learner@example.com"}
        mock_client.User.get_metadata_by_token.return_value = response

        provider = MagicAuthProvider()
        profile = provider.fetch_user_profile("did:ethr:abc", "fake.did.token")

        assert profile is not None
        assert profile.email == "learner@example.com"

    def test_fetch_user_profile_no_email_returns_none(self, mock_client):
        response = MagicMock()
        response.data = {}
        mock_client.User.get_metadata_by_token.return_value = response

        provider = MagicAuthProvider()
        assert provider.fetch_user_profile("did:ethr:abc", "fake.did.token") is None

    def test_fetch_user_profile_no_credential_returns_none(self):
        provider = MagicAuthProvider()
        assert provider.fetch_user_profile("did:ethr:abc") is None
