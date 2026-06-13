# AI Workspace for Noni

This directory contains session artifacts, recovery logs, and process documentation for AI agent coding sessions.

## Directory Structure

```
.ai/
├── sessions/           # Session State Agent checkpoints
│   └── YYYY-MM-DD_topic.md
├── recovery/           # Recovery Agent failure logs
│   └── YYYY-MM-DD_failure.md
└── README.md           # This file
```

## Sessions

Session State Agent writes checkpoints here:
- `active_checkpoint.md` — Current session in progress
- `YYYY-MM-DD_topic.md` — Completed session artifacts

Each session artifact contains:
- Decisions made
- Files changed
- Lessons learned
- Task graph status
- Next steps

## Recovery

Recovery Agent writes failure diagnoses here:
- `YYYY-MM-DD_failure.md` — Gate failure diagnosis and fix attempt log

Each failure log contains:
- Failure category (from error-taxonomy)
- Gate that failed
- Diagnosis
- Fix attempts (max 3)
- Escalation report (if auto-fix failed)

## Usage

- **Session Open**: Read most recent session for context
- **Session Close**: Write checkpoint with timestamp
- **Recovery**: Classify failure, attempt fix, log result

---

*Managed by Session State Agent and Recovery Agent per The Process.*
