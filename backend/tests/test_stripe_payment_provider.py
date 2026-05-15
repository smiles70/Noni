"""Sprint B4: StripePaymentProvider unit tests.

We do not hit Stripe's API here; the focus is the provider's contract:
   - it lazy-imports the real `stripe` SDK
   - it forwards the right shape of args to `checkout.Session.create`
   - it verifies webhooks via `stripe.Webhook.construct_event` and only
     accepts events whose signature header matches
   - it fails closed (raises WebhookVerificationError) on missing
     signature, malformed body, or signature mismatch

Approach: inject a fake `stripe` module into `sys.modules` BEFORE the
provider's lazy `import stripe` happens, configure settings, then
exercise the provider. The fake records the calls it received.
"""

from __future__ import annotations

import sys
import types
import uuid
from typing import Any

import pytest

from backend.services.payment_provider import (
    StripePaymentProvider,
    WebhookVerificationError,
)


def _install_fake_stripe(
    *,
    session_id: str = "cs_test_abc",
    session_url: str = "https://checkout.stripe.test/abc",
    webhook_event: dict[str, Any] | None = None,
    webhook_raises: Exception | None = None,
) -> types.SimpleNamespace:
    """Build a stripe-shaped fake and put it in sys.modules.

    Returns the fake so tests can assert on captured arguments.
    """
    captured: dict[str, Any] = {}

    class _Session:
        def __init__(self, **kwargs: Any) -> None:
            self.id = session_id
            self.url = session_url

    class _CheckoutSessionAPI:
        @staticmethod
        def create(**kwargs: Any) -> _Session:
            captured["create_kwargs"] = kwargs
            return _Session()

    class _Webhook:
        @staticmethod
        def construct_event(
            payload: bytes, sig_header: str, secret: str
        ) -> dict[str, Any]:
            captured["construct_event"] = {
                "payload": payload,
                "sig_header": sig_header,
                "secret": secret,
            }
            if webhook_raises is not None:
                raise webhook_raises
            return webhook_event or {
                "id": "evt_test_1",
                "type": "checkout.session.completed",
                "data": {"object": {"id": "cs_test_abc"}},
            }

    fake = types.SimpleNamespace(
        api_key=None,
        checkout=types.SimpleNamespace(Session=_CheckoutSessionAPI),
        Webhook=_Webhook,
        _captured=captured,
    )
    sys.modules["stripe"] = fake  # type: ignore[assignment]
    return fake


@pytest.fixture
def stripe_env(monkeypatch):
    """Provide non-empty Stripe secrets so the provider initializes."""
    from backend.core import config as cfg

    monkeypatch.setattr(cfg.settings, "STRIPE_SECRET_KEY", "sk_test_dummy")
    monkeypatch.setattr(cfg.settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_dummy")
    yield


def _provider() -> StripePaymentProvider:
    return StripePaymentProvider()


# ---- checkout session ------------------------------------------------------


def test_create_checkout_session_returns_session_id_and_url(stripe_env):
    fake = _install_fake_stripe()
    purchase_id = uuid.uuid4()
    buyer_id = uuid.uuid4()

    session = _provider().create_checkout_session(
        product_code="modules_4_5",
        price_id="price_test_123",
        amount_cents=4900,
        currency="usd",
        buyer_account_id=buyer_id,
        purchase_id=purchase_id,
        success_url="https://app.example.test/purchase/success",
        cancel_url="https://app.example.test/purchase/cancel",
        is_gift=False,
    )

    assert session.provider_session_id == "cs_test_abc"
    assert session.url.startswith("https://")

    kwargs = fake._captured["create_kwargs"]
    assert kwargs["mode"] == "payment"
    assert kwargs["line_items"] == [{"price": "price_test_123", "quantity": 1}]
    # `{CHECKOUT_SESSION_ID}` placeholder is what Stripe substitutes; we
    # forward it verbatim so the success page can show the session.
    assert "{CHECKOUT_SESSION_ID}" in kwargs["success_url"]
    assert kwargs["cancel_url"] == "https://app.example.test/purchase/cancel"

    # Metadata is the only thing tying a Stripe event back to our purchase.
    # Both the session AND the payment_intent need it (refund events come
    # through the PI, not the session).
    for md in (kwargs["metadata"], kwargs["payment_intent_data"]["metadata"]):
        assert md["product_code"] == "modules_4_5"
        assert md["buyer_account_id"] == str(buyer_id)
        assert md["purchase_id"] == str(purchase_id)
        assert md["is_gift"] == "false"


def test_create_checkout_session_marks_gifts_as_such(stripe_env):
    fake = _install_fake_stripe()
    _provider().create_checkout_session(
        product_code="modules_4_5",
        price_id="price_test_123",
        amount_cents=4900,
        currency="usd",
        buyer_account_id=uuid.uuid4(),
        purchase_id=uuid.uuid4(),
        success_url="https://x/s",
        cancel_url="https://x/c",
        is_gift=True,
    )
    kwargs = fake._captured["create_kwargs"]
    assert kwargs["metadata"]["is_gift"] == "true"
    assert kwargs["payment_intent_data"]["metadata"]["is_gift"] == "true"


# ---- webhook verification --------------------------------------------------


def test_verify_webhook_returns_event_when_signature_valid(stripe_env):
    fake = _install_fake_stripe(
        webhook_event={
            "id": "evt_xyz",
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_xyz", "status": "complete"}},
        }
    )
    body = b'{"id":"evt_xyz","type":"checkout.session.completed"}'
    event = _provider().verify_webhook(body, "t=1,v1=deadbeef")
    assert event.event_id == "evt_xyz"
    assert event.event_type == "checkout.session.completed"
    assert event.payload == {"id": "cs_xyz", "status": "complete"}

    # Forwarded the raw body + signature verbatim so Stripe SDK can do
    # constant-time HMAC compare.
    captured = fake._captured["construct_event"]
    assert captured["payload"] == body
    assert captured["sig_header"] == "t=1,v1=deadbeef"
    assert captured["secret"] == "whsec_test_dummy"


def test_verify_webhook_rejects_missing_signature_header(stripe_env):
    _install_fake_stripe()
    with pytest.raises(WebhookVerificationError, match="missing Stripe-Signature"):
        _provider().verify_webhook(b"{}", None)


def test_verify_webhook_rejects_when_stripe_raises_signature_error(stripe_env):
    _install_fake_stripe(webhook_raises=RuntimeError("signature mismatch"))
    with pytest.raises(WebhookVerificationError, match="signature mismatch"):
        _provider().verify_webhook(b"{}", "t=1,v1=bad")


def test_verify_webhook_rejects_when_stripe_raises_malformed_body(stripe_env):
    _install_fake_stripe(webhook_raises=ValueError("invalid JSON"))
    with pytest.raises(WebhookVerificationError, match="invalid JSON"):
        _provider().verify_webhook(b"not json", "t=1,v1=ok")


# ---- bootstrap guards ------------------------------------------------------


def test_provider_refuses_to_init_without_secret_key(monkeypatch):
    from backend.core import config as cfg

    monkeypatch.setattr(cfg.settings, "STRIPE_SECRET_KEY", "")
    monkeypatch.setattr(cfg.settings, "STRIPE_WEBHOOK_SECRET", "whsec_test_dummy")
    _install_fake_stripe()
    with pytest.raises(RuntimeError, match="STRIPE_SECRET_KEY"):
        StripePaymentProvider()


def test_provider_refuses_to_init_without_webhook_secret(monkeypatch):
    from backend.core import config as cfg

    monkeypatch.setattr(cfg.settings, "STRIPE_SECRET_KEY", "sk_test_dummy")
    monkeypatch.setattr(cfg.settings, "STRIPE_WEBHOOK_SECRET", "")
    _install_fake_stripe()
    with pytest.raises(RuntimeError, match="STRIPE_WEBHOOK_SECRET"):
        StripePaymentProvider()
