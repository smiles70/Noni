# Golden Landing Flow — "First Safe Understanding"

**Status**: Canonical product spec.
**Owner**: Product / geragogy lead.
**Related ADR**: `docs/decisions/0001-landing-flow.md`

## Purpose

Define the minimal, safe, cognitively respectful path from first visit to first real value.

## Non-negotiable constraints

- Older-adult appropriate
- Geragogy-aligned
- Zero pressure
- Fully reversible
- No hidden commitments
- No design or visual assumptions
- Compatible with the ISCS-governed architecture

## Steps

### Step 0 — Arrival (Uncommitted Entry)

- **User state**: Curious or uncertain; possible anxiety about AI or "doing something wrong"; no intent to commit yet.
- **System responsibility**: Require nothing. Demand nothing. Explain nothing yet.
- **User agency**: Can leave immediately with no loss. Has not been assessed, tracked, or obligated.
- **Exit safety**: Full exit, no penalty.

### Step 1 — What This Is (Orientation Without Action)

- **User state**: Wants to know "What is this?"; assessing risk, tone, credibility.
- **System responsibility**: Explain what Noni is in plain language. Clarify what it does and does not do. Set calm expectations.
- **User agency**: Passive reading only. No decisions required.
- **Exit safety**: Full exit, no penalty.

### Step 2 — Is This For Me? (Self-Assessment, Not Testing)

- **User state**: Internally evaluating relevance; comparing this to past technology experiences.
- **System responsibility**: Describe who Noni is designed for. Normalize uncertainty and lack of experience. Explicitly remove any expectation of prior knowledge.
- **User agency**: User decides privately if this feels appropriate. No input required.
- **Exit safety**: Full exit, no penalty.

### Step 3 — Safety & Control (Risk Reduction)

- **User state**: Concerned about mistakes, privacy, or being overwhelmed.
- **System responsibility**: State clearly that nothing happens automatically; all actions are previewed; stopping is always allowed. Reinforce user authority.
- **User agency**: Permission-based continuation only.
- **Exit safety**: Full exit, no penalty.

### Step 4 — Low-Commitment Choice (Invitation, Not CTA)

- **User state**: Ready to explore, but not to commit.
- **System responsibility**: Offer a gentle option to continue. Emphasize reversibility and lack of obligation.
- **User agency**: Optional choice to explore further. **First explicit action**, but still low-stakes.
- **Exit safety**: Declining has no downside. No data dependency created.

### Step 5 — First Guided Interaction (Protected Entry)

- **User state**: Slightly engaged; testing whether the system feels safe.
- **System responsibility**: Provide a single, simple, guided interaction. No branching. No complex decisions. No time pressure.
- **User experience**: User sees Claude respond in a controlled, explain-as-you-go way. Nothing is asked of the user except observation or a simple acknowledgment.
- **Exit safety**: User can stop immediately. Nothing persists unless they choose later.

### Step 6 — First Safe Win (Value Before Commitment)

- **User state**: Experiencing usefulness for the first time; beginning to form confidence.
- **System responsibility**: Make the value explicit ("This is what learning with Noni feels like"). Reflect success back to the user without praise or judgment.
- **User outcome**: Understanding achieved. No identity threat. No dependency created.
- **Exit safety**: User can leave feeling informed, not enrolled.

### Step 7 — Optional Continuation (After Value)

- **User state**: Calm, informed, confident enough to decide.
- **System responsibility**: Offer next steps only now. Make clear that learning can remain gradual.
- **User agency**: Choice to continue, pause, or leave. All options equally valid.
- **Exit safety**: Full exit remains safe and respected.

## Notes

- This document defines the **flow**. UI, design, and final user-facing copy are explicitly out of scope here and belong to a future "Copy & Visual Design" sprint.
- The structured representation lives in `backend/models/landing.py` and is served from `/api/landing/steps`.
