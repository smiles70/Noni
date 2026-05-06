# Noni

A geragogy-grounded AI learning system for older adults.

---

## 1. Project Purpose

Noni provides structured, respectful learning experiences designed specifically for older adults. The system prioritizes **cognitive safety**, **dignity**, and **autonomy** over speed or engagement metrics.

The design philosophy centers on:
- **Predictable experiences**: No surprises, no sudden changes
- **User-controlled pacing**: Learners set their own rhythm
- **Reversible progress**: Any advancement can be undone
- **Cognitive load management**: Complexity is introduced gradually and explicitly

---

## 2. Technology Stack Rationale

### Backend
- **Python 3.11+**: Type hints, modern async support, enterprise standard
- **FastAPI**: Performance, automatic API documentation, Pydantic integration
- **Pydantic**: Runtime validation, clear data contracts
- **SQLAlchemy**: Battle-tested ORM, explicit control over database operations
- **PostgreSQL**: ACID compliance, audit trail support, relational integrity

### Frontend
- **React + TypeScript (strict)**: Component boundaries, compile-time safety
- **Passive rendering only**: No business logic, no state management
- All state transitions governed by backend authority

### Infrastructure
- **Docker**: Reproducible environments, clear dependency boundaries
- **Environment-based configuration**: Twelve-factor methodology, no code changes for deployment

### Explicit Non-Choices
- **No serverless orchestration**: Complexity hiding leads to unpredictable behavior
- **No frontend-controlled state**: Authority must reside in auditable backend code
- **No NoSQL defaults**: ACID properties required for user progress data
- **No growth frameworks**: Premature abstraction creates technical debt

---

## 3. Architectural Principles

### Backend Authority
All progression decisions live in backend code. The frontend never determines user state, advancement, or completion status.

### Content as Data
Learning content is data, not logic. Content blocks define what to present; the system governs when and how.

### Reversibility
All user advancement is reversible. A learner can return to any previous state without penalty or data loss.

### Explicit Over Implicit
No automated actions without explicit review. No hidden state changes. No surprise transitions.

### Calm Experience Design
- No countdown timers
- No urgency framing
- No gamification pressure
- No interruption-based notifications
- Clear, consistent navigation

---

## 4. Geragogy Grounding

Noni is built on principles of geragogy (learning theory for older adults):

- **Respect for autonomy**: Learners control their journey
- **Acknowledgment of experience**: Content honors life experience and wisdom
- **Cognitive pacing**: Information presented in digestible segments
- **Error tolerance**: Mistakes are learning opportunities, not failures
- **Accessibility by design**: Not an add-on, but a foundational requirement

---

## 5. Non-Goals

This system explicitly does **NOT**:

- Optimize for "daily active users" or engagement metrics
- Use gamification, leaderboards, or competitive elements
- Employ dark patterns (infinite scroll, variable rewards, social pressure)
- Make automated decisions about user advancement without explicit review
- Store or process data without clear user benefit and consent
- Prioritize feature velocity over stability and safety

---

## 6. Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL 15+ (or Docker for local development)

### Initial Setup

```bash
# 1. Clone and enter repository
cd Noni

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
# Or: pip install -e ".[dev]"

# 4. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 5. Start database (optional - Docker)
docker-compose up -d db

# 6. Run application
uvicorn backend.app.main:app --reload
```

### Verification
```bash
# Health check
curl http://localhost:8000/health

# Run tests
pytest
```

---

## 7. Governance Philosophy

### Backend Authority
The Interface State Governor (`backend/core/interface_state_governor.py`) is the single source of truth for all user state. No frontend code may:
- Modify user progression state
- Determine advancement eligibility
- Store authoritative user data

### User Dignity
Every feature is evaluated against these questions:
- Does this respect the user's autonomy?
- Does this protect cognitive safety?
- Is this calm and predictable?
- Can the user undo this action?

### Audit and Maintainability
All state changes are:
- Logged with explicit reasons
- Reversible
- Reviewable by human operators
- Tested with clear expectations

---

## 8. Architectural Rules (Non-Negotiable)

See `ARCHITECTURE.md` for the complete non-negotiable architectural rules.

Key principles:
1. **Backend Authority**: All state decisions in backend code
2. **Frontend Passivity**: Frontend renders, backend governs
3. **Content/Data Separation**: Content is data, logic is code
4. **Reversibility**: All advancement can be undone
5. **No Urgency**: No timers, pressure, or artificial scarcity
6. **No Dark Patterns**: No psychological manipulation
7. **Explicit Review**: No automated state changes without human review
8. **Cognitive Safety First**: Design respects older adult cognitive needs

---

## 9. Project Structure

```
backend/
  app/           # FastAPI application entry
  core/          # Configuration, state governor
  content/       # Content data (not logic)
  models/        # Database models
  api/routes/    # API endpoints
  tests/         # Test suite
frontend/
  src/           # React components (passive only)
scripts/         # Bootstrap and utility scripts
```

---

## License

Proprietary - Noni Engineering Team

---

*Built with respect for the humans who will use it.*
