# Noni Architecture: Non-Negotiable Rules

This document defines the foundational architectural constraints for Noni. These rules are **immutable** and apply to all code, content, and system evolution.

---

## 1. Backend Authority

**RULE**: All progression decisions live in backend code.

**RATIONALE**: Frontend code is ephemeral, harder to audit, and subject to manipulation. User state must be governed by persistent, tested, auditable backend systems.

**ENFORCEMENT**:
- The `InterfaceStateGovernor` is the sole authority for user state
- Frontend may request, but never determine, state transitions
- All state changes require backend validation and logging

---

## 2. Frontend Passivity

**RULE**: The frontend NEVER determines user state.

**RATIONALE**: UI code changes frequently, runs on untrusted clients, and cannot be reliably audited.

**ENFORCEMENT**:
- Frontend components render state from backend API responses
- No local storage of authoritative user data
- No client-side logic for progression determination
- All API calls for state changes are requests, not commands

---

## 3. Content/Data Separation

**RULE**: Content is data, not logic.

**RATIONALE**: Learning materials should be separable from system behavior. Content changes should not require code changes.

**ENFORCEMENT**:
- Content blocks define presentation (what to show)
- System code governs timing and transitions (when/how)
- Content stored as structured data (JSON, YAML, database records)
- No business logic embedded in content files

---

## 4. Reversibility

**RULE**: All user advancement is reversible.

**RATIONALE**: Learning is non-linear. Users must be able to review, pause, or revert without penalty.

**ENFORCEMENT**:
- Every state transition has an inverse operation
- User history is preserved, not overwritten
- "Back" is always available
- No destructive operations on user progress data

---

## 5. No Urgency Framing

**RULE**: No timers, countdowns, or artificial pressure.

**RATIONALE**: Cognitive load from time pressure disproportionately affects older adults. Learning requires reflection time.

**ENFORCEMENT**:
- No countdown timers
- No "limited time" messaging
- No speed-based scoring
- No real-time competitive elements
- Pacing entirely user-controlled

---

## 6. No Dark Patterns

**RULE**: No psychological manipulation or deceptive design.

**RATIONALE**: Users must make informed, unpressured decisions. Manipulation violates autonomy and dignity.

**ENFORCEMENT**:
- No variable reward schedules
- No hidden costs or consequences
- No confusing navigation
- No false scarcity messaging
- Clear, honest communication in all UI copy

---

## 7. Explicit Review

**RULE**: No automated actions without explicit review.

**RATIONALE**: Users must understand and consent to system behavior. Surprise actions erode trust.

**ENFORCEMENT**:
- Significant state changes require explicit confirmation
- Automated suggestions are clearly labeled as such
- Review steps are skippable only by explicit user choice
- Batch operations are previewed before execution

---

## 8. Cognitive Safety First

**RULE**: All design must respect older-adult cognitive needs.

**RATIONALE**: The target population has specific accessibility and cognitive load requirements.

**ENFORCEMENT**:
- Consistent navigation patterns
- Clear information hierarchy
- Large, readable typography
- High contrast by default
- No flashing or sudden visual changes
- Memory aids and context preservation
- Error messages that guide, not blame

---

## 9. Auditability

**RULE**: All system behavior must be auditable.

**RATIONALE**: Enterprise systems require accountability. Debugging, compliance, and improvement all require clear records.

**ENFORCEMENT**:
- All state transitions logged with timestamp, reason, and actor
- API requests logged with parameters and outcomes
- Content version tracking
- Database migrations are reversible and documented

---

## 10. Long-Term Maintainability

**RULE**: Code must remain understandable and modifiable for years.

**RATIONALE**: This is a production system with long-term responsibility to users.

**ENFORCEMENT**:
- Explicit over clever
- Well-structured tests for all logic
- Documentation of intent, not just mechanics
- No experimental or deprecated dependencies in production
- Regular dependency updates with clear rollback paths

---

## Violation Policy

Any code that violates these rules **must not be merged**.

If business requirements appear to conflict with these rules:
1. Re-examine the requirement
2. Propose alternatives that preserve principles
3. Escalate to architecture review if necessary
4. Never silently compromise on safety or dignity

---

*These rules exist to protect users and the integrity of the system. They are not obstacles to work around, but guardrails to work within.*
