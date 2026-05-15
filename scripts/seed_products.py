"""Idempotent product seeding for production.

Tests seed their own products; staging/prod databases do not. This script
ensures the canonical `modules_4_5` row exists and that its
`stripe_price_id` matches `STRIPE_PRICE_ID_MODULES_4_5` from the
environment.

Usage:
    python -m scripts.seed_products

Safe to run repeatedly. On each run:
- creates the row if missing
- updates `stripe_price_id` if it drifted from settings
- does not touch other columns (`display_name`, `price_cents`,
  `active`, etc.) so you can edit them by hand and not lose changes

Pricing source of truth:
    Stripe dashboard -> Products -> "Modules 4 & 5" -> price ID

The price (amount_cents / currency) on the row is informational; the
real charge is whatever Stripe associates with the price_id.
"""

from __future__ import annotations

import sys

from backend.core.config import settings
from backend.core.database import SessionLocal
from backend.models.billing import Product

CANONICAL = {
    "code": "modules_4_5",
    "display_name": "Modules 4 & 5: Building & Composing Claude Skills",
    "price_cents": 4900,  # $49.00, informational; Stripe is source of truth
    "currency": "usd",
}


def main() -> int:
    target_price_id = settings.STRIPE_PRICE_ID_MODULES_4_5 or None
    if not target_price_id:
        print(
            "WARN: STRIPE_PRICE_ID_MODULES_4_5 is empty. The row will be "
            "created/kept but checkout will fail until you set this env var "
            "to the Stripe price ID (price_xxx).",
            file=sys.stderr,
        )

    with SessionLocal() as db:
        existing = db.query(Product).filter(Product.code == CANONICAL["code"]).one_or_none()
        if existing is None:
            row = Product(
                **CANONICAL,
                stripe_price_id=target_price_id,
                active=True,
                content_version=1,
            )
            db.add(row)
            db.commit()
            print(
                f"created: products.code={CANONICAL['code']!r} "
                f"stripe_price_id={target_price_id!r}",
            )
            return 0

        if target_price_id and existing.stripe_price_id != target_price_id:
            old = existing.stripe_price_id
            existing.stripe_price_id = target_price_id
            db.commit()
            print(
                f"updated: products.code={CANONICAL['code']!r} "
                f"stripe_price_id {old!r} -> {target_price_id!r}",
            )
            return 0

        print(
            f"unchanged: products.code={CANONICAL['code']!r} "
            f"stripe_price_id={existing.stripe_price_id!r}",
        )
        return 0


if __name__ == "__main__":
    sys.exit(main())
