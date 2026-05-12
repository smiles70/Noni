/**
 * Unit tests for `api/oauth.ts`.
 *
 * The OAuth helpers are tiny but security-relevant: parsing the hash
 * incorrectly could either lose a valid token (sign-in silently fails)
 * or accept input that isn't a real Supabase callback (e.g. opening the
 * app with a crafted #access_token=... in the URL).
 *
 * `parseOAuthFragment` is pure and the cheap thing to pin. The redirect
 * helper is exercised only superficially because jsdom is not in scope
 * for this project (vitest.config sets environment: "node").
 */
import { describe, expect, it } from "vitest";

import { parseOAuthFragment } from "../oauth";

describe("parseOAuthFragment", () => {
  it("returns null for empty / null-ish input", () => {
    expect(parseOAuthFragment("")).toBeNull();
    expect(parseOAuthFragment("#")).toBeNull();
  });

  it("returns null when the fragment has no access_token", () => {
    expect(parseOAuthFragment("#refresh_token=rt&expires_in=3600")).toBeNull();
    expect(parseOAuthFragment("#error=access_denied")).toBeNull();
  });

  it("parses a full supabase callback fragment", () => {
    const hash =
      "#access_token=eyJhbGciOi.JWT.body" +
      "&refresh_token=rt-abc" +
      "&expires_in=3600" +
      "&token_type=bearer";
    const parsed = parseOAuthFragment(hash);
    expect(parsed).not.toBeNull();
    expect(parsed!.accessToken).toBe("eyJhbGciOi.JWT.body");
    expect(parsed!.refreshToken).toBe("rt-abc");
    expect(parsed!.expiresIn).toBe(3600);
    expect(parsed!.tokenType).toBe("bearer");
  });

  it("tolerates the fragment with or without leading #", () => {
    const a = parseOAuthFragment("#access_token=x");
    const b = parseOAuthFragment("access_token=x");
    expect(a?.accessToken).toBe("x");
    expect(b?.accessToken).toBe("x");
  });

  it("leaves optional fields undefined when missing", () => {
    const parsed = parseOAuthFragment("#access_token=only");
    expect(parsed).not.toBeNull();
    expect(parsed!.refreshToken).toBeUndefined();
    expect(parsed!.expiresIn).toBeUndefined();
    expect(parsed!.tokenType).toBeUndefined();
  });

  it("does not coerce a non-numeric expires_in into NaN", () => {
    const parsed = parseOAuthFragment("#access_token=t&expires_in=soon");
    expect(parsed).not.toBeNull();
    expect(parsed!.expiresIn).toBeUndefined();
  });
});
