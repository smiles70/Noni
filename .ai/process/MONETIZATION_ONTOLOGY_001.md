# MONETIZATION-001 Ontology

**Process:** v9.51  
**Intake:** `.ai/intake/2026-08-27-monetization-001.md`  
**Purpose:** Formalize entities and traceability for the sustainability research.

---

## New entities

- `SourceArtifact`: `SRC-KHAN-AR-24`, `SRC-OATS-AT&T`, `SRC-OATS-JPM`, `SRC-GETSETUP-GSB`, `SRC-AARP-2025`, `SRC-DUOLINGO-10K`, `SRC-EY-2026`, `SRC-ELDERCLASS`, `SRC-RENDEVER`, `SRC-SENIOR-SHIELD`
- `Requirement`: `REQ-MON-001` (free core), `REQ-MON-002` (sustainable revenue), `REQ-MON-003` (B2B2C/sponsorship), `REQ-MON-004` (no ads), `REQ-MON-005` (no subscription dark patterns)
- `Persona`: `PERSONA-B2B-Buyer`, `PERSONA-Learner-LowIncome`
- `Journey`: `JOURNEY-B2B2C-Access`
- `Capability`: `CAP-OrgLicense`, `CAP-AccessCode`, `CAP-InstitutionalBilling`
- `Decision`: `DEC-MON-001` (for-profit B2B2C-first hybrid)
- `Evidence`: `EVI-MON-001`–`EVI-MON-012`
- `Assumption`: `ASM-MON-001` (B2B buyers exist), `ASM-MON-002` (per-seat price viable)
- `Gap`: `GAP-MON-001` (no B2B pricing), `GAP-MON-002` (no sales/pilot partner), `GAP-MON-003` (no unit economics model)

## Traceability summary

- `SRC-AARP-2025` `evidenced_by` `EVI-MON-001`.
- `SRC-KHAN-AR-24` `evidenced_by` `EVI-MON-002`.
- `SRC-GETSETUP-GSB` `evidenced_by` `EVI-MON-003`.
- `SRC-OATS-AT&T`, `SRC-OATS-JPM`, `SRC-OATS-VERIZON`, `SRC-OATS-TMOBILE` `evidenced_by` `EVI-MON-004`.
- `SRC-DUOLINGO-10K` `evidenced_by` `EVI-MON-005`.
- `EVI-MON-001`, `EVI-MON-002`, `EVI-MON-004` `defines` `REQ-MON-001`.
- `EVI-MON-003`, `EVI-MON-005` `defines` `REQ-MON-002`.
- `EVI-MON-003`, `EVI-MON-004` `defines` `REQ-MON-003`.
- `EVI-MON-001` `defines` `REQ-MON-004` and `REQ-MON-005`.
- `REQ-MON-001` `serves` `PERSONA-Learner-55Plus` and `PERSONA-Learner-LowIncome`.
- `REQ-MON-003` `serves` `PERSONA-Sponsor-Org`.
- `CAP-SponsorCode` and `CAP-InstitutionalBilling` `implement` `REQ-MON-003`.
- `DEC-MON-001` `decides` `REQ-MON-001`, `REQ-MON-002`, `REQ-MON-003`, `REQ-MON-004`, `REQ-MON-005`.
- `DEC-MON-001` `owned_by` `OWNER-Product`.
- `ASM-MON-001` and `ASM-MON-002` `assumes` `DEC-MON-001`.
- `GAP-MON-001`, `GAP-MON-002`, `GAP-MON-003` `has_gap` `DEC-MON-001`.
