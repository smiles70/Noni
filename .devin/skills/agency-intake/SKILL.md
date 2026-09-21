---
name: agency-intake
description: "Ideation intake for agency bake-offs — accepts dropped screenshots, PDFs, docs, HTML files, and URLs; routes each asset to the right analyzer (ocular pixel analysis for images, text extraction for PDFs, structure parse for HTML, Playwright capture for URLs); produces a structured intake doc plus evidence graph nodes. Invoke at the start of any agency bid work, before ad-agency Stage 1."
---

# Agency Intake — Asset Ingestion & Ideation Intake

The front door for agency work. Kim (or any requester) drops raw material —
screenshots, PDFs, docs, HTML, URLs, pasted copy — and this skill turns it
into a structured intake the `ad-agency` pipeline can bid on.

## Input handling — route by asset type

| Dropped asset | Analyzer | Output |
|---------------|----------|--------|
| Screenshot / image (png, jpg, webp) | **ocular** MCP — `analyze_ui_screenshot` (layout/components) + `extract_text_from_image` (copy capture) | Structured layout + verbatim copy + noted conventions |
| PDF / doc | Read tool; `pdftotext` if binary | Extracted claims, register, proof patterns |
| HTML file or pasted markup | Parse structure — sections, components, CTAs | Page-architecture map (grammar, not skin) |
| URL | Playwright capture (screenshot + DOM) | Evidence snapshot in `.ai/research/agency-bids/evidence/` |
| Pasted copy / brief text | Direct | Persona + goal signals into the intake doc |

**Pixel-level review is mandatory for every image** — ocular analyze pass,
not a glance. Record what the layout *does*, not what it looks like.

## Output contract

Every intake produces `.ai/intake/YYYY-MM-DD-pN-<slug>-agency.md` containing:

1. **Problem statement** — which surface, which persona (per AGENTS.md dual-
   audience rule), what the requester asked for, what success looks like.
2. **Asset register** — every dropped item, its analyzer, its key findings,
   its file path if saved.
3. **Persona declaration** — learner/caregiver (geragogy-bound) vs
   corporate-care (senior-living-agency register). Mixed assets get split
   into per-persona sections; leakage is an auto-fail downstream.
4. **Evidence candidates** — claims/conventions worth graphing; feed
   `knowledge-graph-extraction` after intake.
5. **Bid scope** — which agencies are bidding, how many mocks each, the
   conversion goal.

## Rules

- **No design work in intake.** Intake names the problem; `ad-agency`
  Stage 1+ does the capture→rubric→bid work.
- **Every claim needs a source.** A dropped asset IS the source — record
  where it came from and when.
- **Ambiguity stops the line.** If persona, surface, or scope is unclear,
  ask before drafting — do not guess and bill the owner for rework.
- **Files live in the repo** under `.ai/research/` — never only in chat.
