"""Payment provider abstraction.

See ADR 0021 (pricing) and ADR 0024 (webhook idempotency).

Two concrete providers:
- MockPaymentProvider: returns deterministic IDs and trusts webhook
  payloads marked with `_mock: true`. Used in dev and tests. Never
  enabled in production.
- StripePaymentProvider: real Stripe Checkout + signed webhooks. Lazy-
  imports the `stripe` SDK so tests with the mock provider don't
  require it to be installed.

The provider returns plain dataclasses; route layer never touches
vendor SDKs directly.
"""

from __future__ import annotations

import json
import logging
import secrets
import uuid
from dataclasses import dataclass
from typing import Any, Optional, Protocol

from pybreaker import CircuitBreaker
from prometheus_client import Counter

logger = logging.getLogger(__name__)

# Sprint 27 H3: circuit breaker for Stripe API calls.
_circuit_state_transitions = Counter(
    "noni_circuit_breaker_state_transitions_total",
    "Circuit breaker state transitions",
    ["service", "from_state", "to_state"],
)


class _StripeCircuitListener:
    """Prometheus listener for Stripe circuit breaker state changes."""

    def state_change(self, cb, old_state, new_state):
        _circuit_state_transitions.labels(
            service="stripe",
            from_state=old_state.name,
            to_state=new_state.name,
        ).inc()
        logger.warning(
            "circuit_breaker.state_change",
            extra={
                "service": "stripe",
                "from_state": old_state.name,
                "to_state": new_state.name,
            },
        )


STRIPE_CIRCUIT_BREAKER = CircuitBreaker(
    fail_max=5,
    reset_timeout=30,
    expected_exception=(Exception,),  # stripe.error.* is dynamic
    listeners=[_StripeCircuitListener()],
)


@dataclass(frozen=True)
class CheckoutSession:
    """The minimum a route needs to redirect the buyer to checkout."""

    provider_session_id: str
    url: str


@dataclass(frozen=True)
class WebhookEvent:
    """Provider-agnostic shape of a payment event we act on."""

    event_id: str
    event_type: str  # 'checkout.session.completed' | 'charge.refunded' | other
    payload: dict[str, Any]


class WebhookVerificationError(Exception):
    """Raised on signature mismatch or malformed body. Always fail closed."""


class PaymentProvider(Protocol):
    name: str

    def create_checkout_session(
        self,
        *,
        product_code: str,
        price_id: str,
        amount_cents: int,
        currency: str,
        buyer_account_id: uuid.UUID,
        purchase_id: uuid.UUID,
        success_url: str,
        cancel_url: str,
        is_gift: bool,
    ) -> CheckoutSession: ...

    def verify_webhook(
        self, raw_body: bytes, signature_header: Optional[str]
    ) -> WebhookEvent: ...


# ---------- Mock ----------


class MockPaymentProvider:
    """Deterministic provider for dev and tests.

    `create_checkout_session` returns IDs derived from the purchase id
    so tests can assert on them without external state.

    `verify_webhook` accepts JSON bodies that include a top-level
    `_mock` field set to True. Any other body is rejected.
    """

    name = "mock"

    def create_checkout_session(
        self,
        *,
        product_code: str,
        price_id: str,
        amount_cents: int,
        currency: str,
        buyer_account_id: uuid.UUID,
        purchase_id: uuid.UUID,
        success_url: str,
        cancel_url: str,
        is_gift: bool,
    ) -> CheckoutSession:
        session_id = f"cs_mock_{purchase_id.hex[:12]}"
        url = (
            f"https://mock-stripe.local/c/{session_id}"
            f"?purchase={purchase_id}&product={product_code}"
        )
        return CheckoutSession(provider_session_id=session_id, url=url)

    def verify_webhook(
        self, raw_body: bytes, signature_header: Optional[str]
    ) -> WebhookEvent:
        try:
            body = json.loads(raw_body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise WebhookVerificationError(f"malformed body: {e}") from e
        if not isinstance(body, dict) or body.get("_mock") is not True:
            raise WebhookVerificationError("missing _mock flag")
        event_id = body.get("id") or f"evt_mock_{secrets.token_hex(8)}"
        event_type = body.get("type")
        if not isinstance(event_type, str):
            raise WebhookVerificationError("missing event type")
        payload = body.get("data", {}).get("object", {})
        if not isinstance(payload, dict):
            raise WebhookVerificationError("missing payload object")
        return WebhookEvent(event_id=event_id, event_type=event_type, payload=payload)


# ---------- Stripe (lazy import) ----------


class StripePaymentProvider:
    """Real Stripe provider. Requires `stripe` SDK and configured secrets."""

    name = "stripe"

    def __init__(self) -> None:
        from backend.core.config import settings

        try:
            import stripe  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "stripe SDK not installed. Add 'stripe' to requirements.txt "
                "or set AUTH_PROVIDER=mock for development."
            ) from e

        if not settings.STRIPE_SECRET_KEY:
            raise RuntimeError("STRIPE_SECRET_KEY is empty")
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise RuntimeError("STRIPE_WEBHOOK_SECRET is empty")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        self._stripe = stripe
        self._webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    @STRIPE_CIRCUIT_BREAKER
    def create_checkout_session(
        self,
        *,
        product_code: str,
        price_id: str,
        amount_cents: int,
        currency: str,
        buyer_account_id: uuid.UUID,
        purchase_id: uuid.UUID,
        success_url: str,
        cancel_url: str,
        is_gift: bool,
    ) -> CheckoutSession:
        session = self._stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url + "?cs={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            metadata={
                "product_code": product_code,
                "buyer_account_id": str(buyer_account_id),
                "purchase_id": str(purchase_id),
                "is_gift": "true" if is_gift else "false",
            },
            payment_intent_data={
                "metadata": {
                    "product_code": product_code,
                    "buyer_account_id": str(buyer_account_id),
                    "purchase_id": str(purchase_id),
                    "is_gift": "true" if is_gift else "false",
                }
            },
        )
        return CheckoutSession(provider_session_id=session.id, url=session.url)

    @STRIPE_CIRCUIT_BREAKER
    def verify_webhook(
        self, raw_body: bytes, signature_header: Optional[str]
    ) -> WebhookEvent:
        if not signature_header:
            raise WebhookVerificationError("missing Stripe-Signature header")
        try:
            event = self._stripe.Webhook.construct_event(
                raw_body, signature_header, self._webhook_secret
            )
        except Exception as e:
            raise WebhookVerificationError(str(e)) from e

        # Runtime schema validation: guard against Stripe API drift
        from backend.models.stripe_event import StripeEvent

        try:
            stripe_event = StripeEvent.model_validate(
                {
                    "id": event["id"],
                    "object": event.get("object", "event"),
                    "api_version": event.get("api_version"),
                    "type": event["type"],
                    "data": event.get("data", {}),
                }
            )
        except Exception as exc:
            raise WebhookVerificationError(
                f"stripe payload validation failed: {exc}"
            ) from exc

        return WebhookEvent(
            event_id=stripe_event.id,
            event_type=stripe_event.type,
            payload=stripe_event.data.get("object", {}),
        )


# ---------- Resolver ----------


def get_payment_provider() -> PaymentProvider:
    """Resolve the configured provider. Mock by default in dev/tests."""
    from backend.core.config import settings

    provider = (settings.PAYMENT_PROVIDER or "mock").lower()
    if provider == "stripe":
        return StripePaymentProvider()
    return MockPaymentProvider()
