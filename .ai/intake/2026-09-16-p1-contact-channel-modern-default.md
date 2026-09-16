# Intake — What is the modern enterprise default contact channel?

**Date:** 2026-09-16
**Status:** in_progress
**Priority:** P1

## Problem statement

Owner observation: none of the top-20 global eLearning companies, no
senior-learning providers, and no top-20 SaaS companies use a button that
launches an email client (`mailto:`). The earlier ticket's mailto
**fallback** shipped but the question of "what is the FAANG/enterprise
best-in-class primary contact path" was never answered end-to-end.

## Research questions

1. If email-client launch is not the modern default, what is? Short
   forms, chat/messaging widgets, scheduling links, voice agents, or
   hybrid?
2. What Claude/Anthropic agents, Google agents, agent skills, or free
   open-source GitHub repos are production-ready for this channel?
3. Does Retell AI (voice agent platform) fit this space — especially
   given our audience of older adults who may prefer a phone call?

## Constraints

- Audience: older adults (55+) and the professionals who serve them.
  Phone/voice is a genuinely expected channel for this demographic —
  unlike typical SaaS.
- Backend: FastAPI on Railway; existing Resend transactional email.
- Geragogy contract on learner surfaces; ADR-0030 annex for marketing.
- Any new vendor needs a decision matrix vs. at least 3 alternatives.

## Deliverable

Research memo at `.ai/research/` with 20+ verified sources (≥5
FAANG-engineering, ≥5 academic, ≥5 industry/security, ≤5 discussion),
decision matrix, edge-case/remediation matrix, then implementation
recommendation for the `/partners` + `/for-communities` contact paths.
