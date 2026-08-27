# GTM-001 Ontology

## Entities

- `SourceArtifact`: `SRC-CENSUS-2025`, `SRC-AARP-2025`, `SRC-AARP-CAREGIVING-2025`, `SRC-GETSETUP-GSB`, `SRC-OATS-PRESS`, `SRC-PEW-2024`, `SRC-CREATINGRESULTS-2025`
- `Persona`: `PERSONA-Learner-55Plus`, `PERSONA-Caregiver-AdultChild`, `PERSONA-B2B-Buyer`
- `Journey`: `JOURNEY-B2C-Purchase`, `JOURNEY-B2B2C-Sales`
- `Capability`: `CAP-YouTube-Content`, `CAP-Facebook-Ads`, `CAP-Email-Nurture`, `CAP-B2B-Outreach`
- `Decision`: `DEC-GTM-001` (dual B2C + B2B2C go-to-market)
- `Evidence`: `EVI-GTM-001` through `EVI-GTM-010`
- `Assumption`: `ASM-GTM-001` (B2C conversion 2-5%), `ASM-GTM-002` (B2B2C price acceptable)
- `Gap`: `GAP-GTM-001` (no ad creative tests), `GAP-GTM-002` (no pilot B2B contracts)

## Traceability

- `SRC-AARP-2025` `evidenced_by` `EVI-GTM-001`.
- `SRC-CENSUS-2025` `evidenced_by` `EVI-GTM-002`.
- `SRC-GETSETUP-GSB` `evidenced_by` `EVI-GTM-003`.
- `EVI-GTM-001`, `EVI-GTM-003` `defines` `DEC-GTM-001`.
- `DEC-GTM-001` `owned_by` `OWNER-Product`.
