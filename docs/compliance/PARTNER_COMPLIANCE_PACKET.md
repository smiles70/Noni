# Partner Compliance Packet — mynaani

For procurement and program reviewers. Everything here is verifiable in our
public pages and repository — we do not ask you to take our word for it.

## Data handling
- What we store, what we never collect, retention and deletion:
  our published privacy page (`/privacy`) — kept current in the repository,
  not a static marketing document.
- Telemetry is server-side allowlisted; no third-party trackers, no ad tech.
- Learner-level data is never exposed to staff: the staff dashboard is
  aggregate-only by design, with a minimum-cohort floor of 5 before any
  engagement counts appear.

## Security posture
- `/.well-known/security.txt` — published disclosure contact.
- Sub-processors and DPA path are listed on the privacy page.
- Authentication is passwordless (email link) — there are no passwords to leak.
- A scoped self-assessment of auth/billing/org surfaces is recorded in
  `.ai/intake/2026-09-06-vuln-scan-org-billing-001.md` (self-assessment;
  not a third-party penetration test).

## PHI statement
mynaani is a learning platform. We do not collect, store, or process
Protected Health Information, and our product is not a covered entity or
business associate under HIPAA. Should a partner's use case ever introduce
health information, we will say so plainly and revisit this statement —
we will not claim compliance we have not demonstrated.

## Business continuity
- Logical backup + restore procedure is drillable on demand; restore
  evidence is retained in the repository when drills run.
- Account export and deletion are self-serve for every learner.
