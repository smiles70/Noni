# Noni — Operator Makefile
#
# Single command surface for development, deploy, secrets, and ops.
# Every target either works locally (no vendor secrets required) or
# no-ops gracefully with a clear message when secrets are absent.
#
# Conventions:
#   - All targets are POSIX-shell compatible (works in WSL, Git Bash, macOS).
#   - Vendor-dependent targets check for required CLIs and secrets first.
#   - No target ever writes a secret to a log or to stdout in plaintext.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.ONESHELL:

ROOT := $(shell git rev-parse --show-toplevel 2>/dev/null || pwd)
INFRA := $(ROOT)/infra
BACKEND := $(ROOT)/backend
FRONTEND := $(ROOT)/frontend

SOPS_FILE := $(INFRA)/.env.prod.sops.yaml
ENV_EXAMPLE := $(INFRA)/.env.example

# ---------- help ----------

.PHONY: help
help:
	@echo "Noni operator targets:"
	@echo ""
	@echo "  Local dev:"
	@echo "    bootstrap            One-time local setup (deps, hooks, local age key)"
	@echo "    up                   Start local stack (Postgres + backend + frontend)"
	@echo "    down                 Stop local stack"
	@echo "    demo                 Bring up the full stack with seeded demo data"
	@echo "    demo-test            Run E2E demo script against local stack"
	@echo ""
	@echo "  Quality:"
	@echo "    test                 Run all tests (backend + frontend unit + e2e)"
	@echo "    test-backend         pytest only"
	@echo "    test-frontend        vitest only"
	@echo "    test-e2e             Playwright only"
	@echo "    lint                 ruff + black --check + isort --check + mypy + eslint"
	@echo "    fmt                  Apply formatters (ruff --fix, black, isort, prettier)"
	@echo ""
	@echo "  Database:"
	@echo "    migrate              alembic upgrade head (against DATABASE_URL_DIRECT)"
	@echo "    migrate-new MSG=...  Create a new Alembic revision"
	@echo "    migrate-down         alembic downgrade -1"
	@echo "    db-shell             psql into local DB"
	@echo "    db-reset             Drop and recreate the local DB"
	@echo ""
	@echo "  Vendor CLIs (one-time):"
	@echo "    check-clis           Verify required CLIs are installed"
	@echo "    cli-auth             Interactive: log in to all vendor CLIs"
	@echo ""
	@echo "  Secrets:"
	@echo "    secrets-bootstrap    Generate age key and encrypt initial .env.prod"
	@echo "    secrets-edit         Open SOPS-encrypted prod env in \$$EDITOR"
	@echo "    secrets-sync         Push secrets to Fly, Cloudflare, Supabase, GitHub"
	@echo "    secrets-rotate KEY=. Rotate a specific secret end-to-end"
	@echo "    secrets-audit        Verify no secret is missing from any vendor"
	@echo ""
	@echo "  Deploy:"
	@echo "    deploy-prod          Full production deploy (supabase + fly + cloudflare)"
	@echo "    smoke-prod           Smoke-test the production endpoints"
	@echo "    smoke-prod-live      Smoke-test with Stripe live mode"
	@echo "    stripe-bootstrap     Create product, price, webhook in Stripe (test mode)"
	@echo "    stripe-promote       Promote Stripe configuration from test to live"
	@echo ""
	@echo "  DR / observability:"
	@echo "    restore-drill        Provision ephemeral DB, restore latest dump, diff"
	@echo "    backup-now           Trigger a one-off pg_dump to R2"
	@echo "    observability-bootstrap  Configure BetterStack monitors"

# ---------- local dev ----------

.PHONY: bootstrap
bootstrap: check-clis
	@echo "==> Installing backend Python deps"
	@cd $(BACKEND) && python -m pip install -r ../requirements.txt -r ../requirements-dev.txt
	@echo "==> Installing frontend Node deps"
	@cd $(FRONTEND) && npm install
	@echo "==> Installing pre-commit hooks"
	@pre-commit install || echo "WARN: pre-commit not installed yet"
	@echo "==> Bootstrap complete. Run 'make up' next."

.PHONY: up
up:
	@echo "==> Starting local stack via docker compose"
	@docker compose -f $(ROOT)/docker-compose.yml up -d
	@echo "==> Stack up. Backend on :8000, frontend on :5173, Postgres on :5432"

.PHONY: down
down:
	@docker compose -f $(ROOT)/docker-compose.yml down

.PHONY: demo
demo: up migrate
	@echo "==> Seeding demo data"
	@$(BACKEND_PYTHON) -m backend.scripts.seed_demo || echo "WARN: seed script not yet implemented (Sprint A2)"

.PHONY: demo-test
demo-test:
	@cd $(FRONTEND) && npx playwright test e2e/demo.spec.ts || echo "WARN: demo spec not yet implemented (Sprint A10)"

# ---------- quality ----------

BACKEND_PYTHON := python
PY_TEST := $(BACKEND_PYTHON) -m pytest

.PHONY: test
test: test-backend test-frontend

.PHONY: test-backend
test-backend:
	@cd $(ROOT) && $(PY_TEST) -q

.PHONY: test-frontend
test-frontend:
	@cd $(FRONTEND) && npm run test:unit --silent

.PHONY: test-e2e
test-e2e:
	@cd $(FRONTEND) && npx playwright test

.PHONY: lint
lint:
	@cd $(ROOT) && ruff check backend && black --check backend && isort --check-only backend && mypy backend
	@cd $(FRONTEND) && npm run lint --silent

.PHONY: fmt
fmt:
	@cd $(ROOT) && ruff check --fix backend && black backend && isort backend
	@cd $(FRONTEND) && npm run fmt --silent || true

# ---------- database ----------

.PHONY: migrate
migrate:
	@cd $(ROOT) && alembic upgrade head

.PHONY: migrate-new
migrate-new:
	@test -n "$(MSG)" || (echo "ERROR: pass MSG=..."; exit 1)
	@cd $(ROOT) && alembic revision --autogenerate -m "$(MSG)"

.PHONY: migrate-down
migrate-down:
	@cd $(ROOT) && alembic downgrade -1

.PHONY: db-shell
db-shell:
	@PGPASSWORD=postgres psql -h localhost -U postgres -d noni

.PHONY: db-reset
db-reset:
	@docker compose -f $(ROOT)/docker-compose.yml down -v
	@docker compose -f $(ROOT)/docker-compose.yml up -d db
	@sleep 3
	@$(MAKE) migrate

# ---------- vendor CLIs ----------

REQUIRED_CLIS := git python node npm pre-commit docker
OPTIONAL_CLIS := gh gcloud supabase flyctl wrangler stripe sops age psql

.PHONY: check-clis
check-clis:
	@echo "==> Required CLIs"
	@for c in $(REQUIRED_CLIS); do \
		if command -v $$c >/dev/null 2>&1; then \
			echo "  OK   $$c"; \
		else \
			echo "  MISS $$c"; \
		fi; \
	done
	@echo "==> Vendor CLIs (needed for Phase B onwards)"
	@for c in $(OPTIONAL_CLIS); do \
		if command -v $$c >/dev/null 2>&1; then \
			echo "  OK   $$c"; \
		else \
			echo "  MISS $$c"; \
		fi; \
	done

.PHONY: cli-auth
cli-auth:
	@echo "==> Logging in to vendor CLIs (each opens a browser tab)"
	@gh auth login        || true
	@gcloud auth login    || true
	@supabase login       || true
	@flyctl auth login    || true
	@wrangler login       || true
	@stripe login         || true

# ---------- secrets ----------

.PHONY: secrets-bootstrap
secrets-bootstrap:
	@bash $(INFRA)/scripts/secrets-bootstrap.sh

.PHONY: secrets-edit
secrets-edit:
	@test -f $(SOPS_FILE) || (echo "ERROR: $(SOPS_FILE) not found; run 'make secrets-bootstrap' first"; exit 1)
	@sops $(SOPS_FILE)

.PHONY: secrets-sync
secrets-sync:
	@bash $(INFRA)/scripts/secrets-sync.sh

.PHONY: secrets-rotate
secrets-rotate:
	@test -n "$(KEY)" || (echo "ERROR: pass KEY=..."; exit 1)
	@bash $(INFRA)/scripts/secrets-rotate.sh "$(KEY)"

.PHONY: secrets-audit
secrets-audit:
	@bash $(INFRA)/scripts/secrets-audit.sh

# ---------- deploy ----------

.PHONY: deploy-prod
deploy-prod:
	@bash $(INFRA)/scripts/deploy-prod.sh

.PHONY: smoke-prod
smoke-prod:
	@bash $(INFRA)/scripts/smoke-prod.sh

.PHONY: smoke-prod-live
smoke-prod-live:
	@bash $(INFRA)/scripts/smoke-prod.sh --live

.PHONY: stripe-bootstrap
stripe-bootstrap:
	@bash $(INFRA)/scripts/stripe-bootstrap.sh

.PHONY: stripe-promote
stripe-promote:
	@bash $(INFRA)/scripts/stripe-promote.sh

# ---------- DR / observability ----------

.PHONY: restore-drill
restore-drill:
	@bash $(INFRA)/scripts/restore-drill.sh

.PHONY: backup-now
backup-now:
	@bash $(INFRA)/scripts/backup-now.sh

.PHONY: observability-bootstrap
observability-bootstrap:
	@bash $(INFRA)/scripts/observability-bootstrap.sh
