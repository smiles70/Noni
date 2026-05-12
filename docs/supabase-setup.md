# Supabase setup (Sprint B2)

Noni delegates identity to Supabase, which in turn delegates to Google.
This document is the exact, ordered checklist to wire a new Supabase
project to a Noni deployment.

You only need to do this once per environment (dev, staging, prod).

## 1. Create the Supabase project

1. Sign in at <https://supabase.com> and create a new project.
2. Pick the region nearest your users; the free tier is fine for staging.
3. Save the database password somewhere safe — Noni does not use it
   directly (we hit Postgres via our own connection string), but you
   will need it if you ever connect with `psql`.

## 2. Enable Google as an auth provider

1. **Project -> Authentication -> Providers -> Google.**
2. Toggle **Enable**.
3. Provide the Google OAuth `client ID` and `client secret` from a
   Google Cloud project (APIs & Services -> Credentials -> OAuth 2.0
   Client). The Google authorized redirect URI must be the URL Supabase
   shows you on this page — copy it verbatim.

## 3. Add Noni as an allowed redirect

Supabase will only redirect back to URLs you explicitly allow.

1. **Authentication -> URL Configuration -> Redirect URLs.**
2. Add the exact origin Noni runs at, e.g.:
   - `http://localhost:5173` (local dev)
   - `https://staging.yourdomain.com`
   - `https://app.yourdomain.com`
3. Set **Site URL** to the production origin.

If a redirect is rejected at sign-in time, this is almost always the
cause.

## 4. Collect the four values Noni needs

From **Project Settings -> API**:

| Noni env var              | Supabase field                                       |
|---------------------------|------------------------------------------------------|
| `SUPABASE_URL`            | "Project URL" (e.g. `https://abcd.supabase.co`)      |
| `SUPABASE_JWT_SECRET`     | "JWT Settings -> JWT Secret"                         |
| `SUPABASE_JWT_AUDIENCE`   | leave as `authenticated` (the Supabase default)      |
| `SUPABASE_JWT_ISSUER`     | `<SUPABASE_URL>/auth/v1` (optional but recommended)  |

The frontend needs **one** of those too:

| Frontend env var          | Value                              |
|---------------------------|------------------------------------|
| `VITE_AUTH_PROVIDER`      | `supabase`                         |
| `VITE_SUPABASE_URL`       | same `https://abcd.supabase.co`    |

## 5. Wire and verify

1. Set the env vars in `.env` (or your secret store).
2. Restart the backend so the new `Settings()` is picked up.
3. Rebuild the frontend (`npm run build`) — Vite bakes `VITE_*` at
   build time, not runtime.
4. From a clean browser session, click **Sign in -> Continue with
   Google**. You should be redirected to Google, then back to Noni,
   then to the landing page with the NavBar showing your email.
5. Inspect the network panel: the POST to `/auth/callback` should be
   201, and the `Set-Cookie` header should set `noni_session`.

## 6. Failure modes (and what they look like)

| Symptom                                              | Likely cause                                   |
|------------------------------------------------------|------------------------------------------------|
| Click "Continue with Google" -> nothing happens      | `VITE_AUTH_PROVIDER` or `VITE_SUPABASE_URL` unset; rebuild required |
| Google says "redirect URI mismatch"                  | Step 2 authorized redirect URI does not match Supabase's |
| Supabase says "redirect not allowed"                 | Origin not in step 3 Redirect URLs list        |
| Round-trip returns to Noni, but stays signed out     | Backend rejected the JWT. Check that `SUPABASE_JWT_SECRET` matches **the same project** as the frontend's URL, and that `SUPABASE_JWT_AUDIENCE`/`SUPABASE_JWT_ISSUER` match the token's claims. The backend logs `supabase_jwt_rejected: <ErrorClass>` to narrow it down. |

## 7. Rotating the JWT secret

Rotate quarterly at minimum, and immediately on suspected compromise.

1. **Supabase -> Project Settings -> API -> JWT Settings -> Rotate.**
2. Update `SUPABASE_JWT_SECRET` in every environment.
3. Existing sessions stay valid (they use Noni's own cookie, not the
   Supabase JWT). Only new sign-ins use the new secret.
