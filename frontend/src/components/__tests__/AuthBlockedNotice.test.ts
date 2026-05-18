/**********************************************************************
 * Unit tests for AuthBlockedNotice.copyForCode.
 *
 * Vitest runs in node mode (no jsdom), so we test the discriminator
 * helper directly rather than rendering. Render coverage is deferred
 * to A4-DOM once jsdom is wired.
 *
 * Contract anchored:
 *   B5  discriminated error handling (per-code copy)
 *   Geragogy: plain language, single recommended action, no raw codes
 **********************************************************************/

import { describe, it, expect } from "vitest";
import { copyForCode } from "../AuthBlockedNotice";

const KNOWN_CODES = [
  "auth.expired",
  "auth.account_deleted",
  "auth.signature_invalid",
  "auth.issuer_mismatch",
  "auth.malformed",
  "auth.subject_missing",
];

describe("copyForCode", () => {
  it("returns expired-specific copy for auth.expired", () => {
    const c = copyForCode("auth.expired");
    expect(c.title).toMatch(/expired/i);
    expect(c.actionLabel).toBe("Sign in again");
  });

  it("returns account-deleted copy for auth.account_deleted", () => {
    const c = copyForCode("auth.account_deleted");
    expect(c.title).toMatch(/no longer available/i);
    expect(c.body.toLowerCase()).toContain("support");
  });

  it("groups verification-failure codes under one copy block", () => {
    const codes = [
      "auth.signature_invalid",
      "auth.issuer_mismatch",
      "auth.malformed",
      "auth.subject_missing",
    ];
    const titles = new Set(codes.map((c) => copyForCode(c).title));
    expect(titles.size).toBe(1);
    expect([...titles][0]).toMatch(/verify/i);
  });

  it("falls back to a safe generic block for unknown codes", () => {
    const c = copyForCode("auth.something_new");
    expect(c.title.length).toBeGreaterThan(0);
    expect(c.actionLabel).toBe("Sign in again");
  });

  it("falls back to a safe generic block for undefined", () => {
    const c = copyForCode(undefined);
    expect(c.title.length).toBeGreaterThan(0);
    expect(c.actionLabel).toBe("Sign in again");
  });

  it("never exposes raw error codes in user-visible copy", () => {
    for (const code of [...KNOWN_CODES, "auth.unknown_xyz"]) {
      const c = copyForCode(code);
      expect(c.title).not.toContain("auth.");
      expect(c.body).not.toContain("auth.");
    }
  });

  it("always offers a single recommended action", () => {
    for (const code of [...KNOWN_CODES, undefined]) {
      const c = copyForCode(code);
      expect(c.actionLabel.length).toBeGreaterThan(0);
    }
  });
});
