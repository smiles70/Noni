"""Gift-lifecycle email contract tests (intake 2026-09-06)."""
import pytest
from unittest.mock import patch
from backend.services import email


def test_send_noops_without_key():
    with patch.object(email.settings, "RESEND_API_KEY", ""):
        assert email.send("a@b.c", "s", "t") is False


def test_send_swallows_provider_errors():
    with patch.object(email.settings, "RESEND_API_KEY", "re_x"),          patch("backend.services.email.httpx.post", side_effect=Exception("down")):
        assert email.send("a@b.c", "s", "t") is False


def test_gift_receipt_copy_is_calm():
    """Geragogy: no exclamation marks, no urgency words."""
    sent = {}
    with patch.object(email.settings, "RESEND_API_KEY", "re_x"),          patch("backend.services.email.httpx.post") as m:
        m.return_value.status_code = 200
        email.send_gift_receipt("giver@x.com", "https://mynaani.com/gift-redeem")
    body = m.call_args[1]["json"]["text"].lower()
    assert "!" not in body
    for w in ("urgent", "immediately", "expires", "act now"):
        assert w not in body
    assert "https://mynaani.com/gift-redeem" in body


def test_gift_claimed_copy_is_calm():
    sent = {}
    with patch.object(email.settings, "RESEND_API_KEY", "re_x"),          patch("backend.services.email.httpx.post") as m:
        m.return_value.status_code = 200
        email.send_gift_claimed("giver@x.com")
    body = m.call_args[1]["json"]["text"]
    assert "!" not in body
    assert "accepted" in body.lower()
