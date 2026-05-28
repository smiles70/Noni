# API Versioning Policy

**Version:** 1.0.0
**Effective Date:** 2026-05-28
**Owner:** Backend Engineering

---

## Versioning Strategy

Noni uses **URL path versioning**: `/api/v1/...` for all public endpoints.

Legacy paths (`/api/...`, `/auth/...`, `/me/...`) are preserved as **302 redirects** with `Deprecation: true` and `Sunset: Sun, 01 Dec 2026 00:00:00 GMT` headers.

---

## Breaking vs Non-Breaking Changes

| Change Type | Classification | Notice Required |
|:---|:---|:---:|
| Adding a new endpoint | Non-breaking | None |
| Adding optional fields to response | Non-breaking | None |
| Adding required fields to request | Breaking | 30 days |
| Removing or renaming a field | Breaking | 90 days |
| Changing field type | Breaking | 90 days |
| Removing an endpoint | Breaking | 6 months |

---

## Deprecation Timeline

| Milestone | Date |
|:---|:---|
| v1.0.0 released | 2026-05-28 |
| Legacy redirects active | Now |
| Legacy paths sunset | 2026-12-01 |
| v2.0.0 (if needed) | TBD -- requires ADR |

---

## Changelog

| Date | Version | Changes |
|:---|:---|:---|
| 2026-05-28 | v1.0.0 | Initial stable API surface under `/api/v1/` |
