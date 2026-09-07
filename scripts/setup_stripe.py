"""Automate Mynaani's Stripe wiring end-to-end (noniSTRIPE companion).

Given a Stripe secret key, this script does every step that does NOT
require a human in a browser:

  1. Creates (or reuses) the product + one-time $39 price -> price_xxx
  2. Creates the webhook endpoint for the target environment and
     captures its signing secret -> whsec_xxx
  3. Writes every env var into Railway via `railway variables set`
  4. Runs scripts.seed_products against that environment
  5. Verifies /api/v1/billing/health reports the expected mode

The ONLY manual step is copying sk_/pk_ keys from the Stripe dashboard —
Stripe intentionally never exposes keys via API.

Usage:
    .venv/bin/python -m scripts.setup_stripe \
        --mode test --env staging \
        --secret-key sk_test_... --publishable-key pk_test_...

    .venv/bin/python -m scripts.setup_stripe \
        --mode live --env production \
        --secret-key sk_live_... --publishable-key pk_live_...

Safety:
- --mode test requires a sk_test_ key; --mode live requires sk_live_.
  Mismatched mode/key aborts before touching anything.
- Idempotent: reuses an existing product/price by lookup metadata and an
  existing webhook endpoint for the same URL rather than duplicating.
- Prints each value it sets; secrets are masked in output.
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
import urllib.parse
import urllib.request

API = "https://api.stripe.com/v1"

ENVIRONMENTS = {
    "staging": {
        "api_url": "https://noni-api-staging.up.railway.app",
        "site": "https://staging.noni-web.pages.dev",
    },
    "production": {
        "api_url": "https://noni-api-production.up.railway.app",
        "site": "https://www.mynaani.com",
    },
}

PRODUCT_NAME = "Mynaani Full Course Access — Modules 2–5"
PRODUCT_DESC = "Full paid course access for one learner. One-time, lifetime."
PRICE_CENTS = 3900
WEBHOOK_EVENTS = ["checkout.session.completed", "charge.refunded"]
LOOKUP_KEY = "mynaani_full_course_v1"


def _stripe(secret: str, method: str, path: str, data: dict | None = None) -> dict:
    """Minimal Stripe API call. Fails loudly on non-2xx."""
    url = f"{API}{path}"
    body = None
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(f"{secret}:".encode()).decode()
    }
    if data is not None:
        body = urllib.parse.urlencode(_flatten(data)).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:500]
        sys.exit(f"Stripe API error {e.code} on {path}: {detail}")


def _flatten(d: dict, prefix: str = "") -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for k, v in d.items():
        key = f"{prefix}[{k}]" if prefix else k
        if isinstance(v, dict):
            out.extend(_flatten(v, key))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                out.append((f"{key}[{i}]", str(item)))
        else:
            out.append((key, str(v)))
    return out


def _mask(v: str) -> str:
    return v[:12] + "..." if len(v) > 12 else "***"


def ensure_price(secret: str) -> str:
    """Reuse an existing price by lookup_key, else create product+price."""
    res = _stripe(
        secret, "GET", f"/prices?lookup_keys[]={LOOKUP_KEY}&limit=1"
    )
    if res.get("data"):
        pid = res["data"][0]["id"]
        print(f"  price: reusing existing {pid}")
        return pid
    res = _stripe(
        secret,
        "POST",
        "/prices",
        {
            "currency": "usd",
            "unit_amount": PRICE_CENTS,
            "lookup_key": LOOKUP_KEY,
            "product_data": {"name": PRODUCT_NAME, "description": PRODUCT_DESC},
        },
    )
    pid = res["id"]
    print(f"  price: created {pid} (${PRICE_CENTS/100:.2f} one-time)")
    return pid


def ensure_webhook(secret: str, url: str) -> str:
    """Reuse the endpoint if it exists for this URL; returns its secret."""
    res = _stripe(secret, "GET", "/webhook_endpoints?limit=100")
    for ep in res.get("data", []):
        if ep.get("url") == url:
            if set(ep.get("enabled_events", [])) >= set(WEBHOOK_EVENTS):
                print(f"  webhook: endpoint already exists ({ep['id']})")
                print(
                    "  NOTE: Stripe does not reveal an existing endpoint's "
                    "secret. If STRIPE_WEBHOOK_SECRET isn't already set from a "
                    "previous run, delete the endpoint in the dashboard and "
                    "re-run, or create it fresh here by removing it first."
                )
                return ""
            # wrong events: update in place
            _stripe(
                secret,
                "POST",
                f"/webhook_endpoints/{ep['id']}",
                {"enabled_events": WEBHOOK_EVENTS},
            )
            print(f"  webhook: updated events on {ep['id']}")
            return ""
    res = _stripe(
        secret,
        "POST",
        "/webhook_endpoints",
        {"url": url, "enabled_events": WEBHOOK_EVENTS},
    )
    secret_wh = res["secret"]
    print(f"  webhook: created {res['id']} -> secret {_mask(secret_wh)}")
    return secret_wh


def railway_set(env: str, pairs: dict[str, str]) -> None:
    for k, v in pairs.items():
        cmd = [
            "railway", "variables", "set", f"{k}={v}",
            "--service", "noni-api",
            "--environment", env,
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)
        status = "ok" if p.returncode == 0 else p.stderr.strip()[:120]
        print(f"  railway {env}: {k}={_mask(v) if 'KEY' in k or 'SECRET' in k else v}  [{status}]")


def verify_health(api_url: str, expect_mode: str) -> None:
    import time

    print("  waiting for deploy, then checking /billing/health ...")
    for _ in range(12):
        time.sleep(15)
        try:
            with urllib.request.urlopen(
                f"{api_url}/api/v1/billing/health", timeout=15
            ) as r:
                h = json.loads(r.read())
            if h.get("provider") == "stripe" and h.get("stripe_mode") == expect_mode:
                print(f"  HEALTH OK: {h}")
                return
        except Exception:
            pass
    print(
        "  WARN: health check did not confirm yet — the Railway deploy may "
        "still be in flight. Re-check "
        f"{api_url}/api/v1/billing/health in a few minutes."
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["test", "live"], required=True)
    ap.add_argument("--env", choices=list(ENVIRONMENTS), required=True)
    ap.add_argument("--secret-key", required=True)
    ap.add_argument("--publishable-key", required=True)
    ap.add_argument("--resend-key", default=None,
                    help="optional re_... key; also sets EMAIL_FROM/FRONTEND_URL")
    ap.add_argument("--seed", action="store_true",
                    help="also run scripts.seed_products via railway run")
    args = ap.parse_args()

    want_prefix = "sk_test_" if args.mode == "test" else "sk_live_"
    if not args.secret_key.startswith(want_prefix):
        sys.exit(f"SAFETY: --mode {args.mode} requires a {want_prefix} key; "
                 f"got {args.secret_key[:8]}...")
    if args.mode == "test" and args.env == "production":
        sys.exit("SAFETY: refusing to set test keys on production.")

    env = ENVIRONMENTS[args.env]
    webhook_url = f"{env['api_url']}/api/v1/billing/stripe-webhook"
    print(f"mode={args.mode} env={args.env} webhook={webhook_url}")

    print("[1/4] product + price")
    price_id = ensure_price(args.secret_key)

    print("[2/4] webhook endpoint")
    wh_secret = ensure_webhook(args.secret_key, webhook_url)

    print("[3/4] railway variables")
    pairs = {
        "PAYMENT_PROVIDER": "stripe",
        "STRIPE_SECRET_KEY": args.secret_key,
        "STRIPE_PUBLISHABLE_KEY": args.publishable_key,
        "STRIPE_PRICE_ID_MODULES_4_5": price_id,
        "STRIPE_SUCCESS_URL": f"{env['site']}/purchase/success",
        "STRIPE_CANCEL_URL": f"{env['site']}/purchase/cancel",
    }
    if wh_secret:
        pairs["STRIPE_WEBHOOK_SECRET"] = wh_secret
    if args.resend_key:
        pairs["RESEND_API_KEY"] = args.resend_key
        pairs["EMAIL_FROM"] = "Mynaani <hello@mynaani.com>"
        pairs["FRONTEND_URL"] = env["site"]
    railway_set(args.env, pairs)

    if args.seed:
        print("[3b] seed_products")
        subprocess.run(
            ["railway", "run", "--service", "noni-api",
             "--environment", args.env,
             "--", ".venv/bin/python", "-m", "scripts.seed_products"],
            check=False,
        )

    print("[4/4] verify")
    verify_health(env["api_url"], args.mode)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
