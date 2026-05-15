# Auth resource library — Clerk + Supabase + relevant standards

Grouped by purpose. Top-of-fold links are the ones to open first; deep-link
paths for Clerk are subject to docs reshuffles, so if a path 404s, drop back
to the section root and search.

## A. Clerk — start here

1. https://clerk.com/docs — docs root
2. https://clerk.com/docs/quickstarts/overview — quickstart index (pick framework)
3. https://clerk.com/docs/quickstarts/react — React SPA quickstart (this is us)
4. https://clerk.com/docs/quickstarts/javascript — vanilla JS, useful for understanding the primitives
5. https://clerk.com/pricing — know the free tier limits before committing
6. https://dashboard.clerk.com/ — where you create the app + get keys
7. https://clerk.com/changelog — what's new / what broke recently
8. https://clerk.com/docs/upgrade-guides/overview — version migration notes

## B. Clerk — React integration

9. https://clerk.com/docs/references/react/overview — React SDK reference
10. https://clerk.com/docs/components/clerk-provider — root provider you wrap your app in
11. https://clerk.com/docs/components/authentication/sign-in — `<SignIn />` drop-in
12. https://clerk.com/docs/components/authentication/sign-up — `<SignUp />` drop-in
13. https://clerk.com/docs/components/user/user-button — avatar + signout menu
14. https://clerk.com/docs/components/control/signed-in — gated rendering
15. https://clerk.com/docs/components/control/signed-out — gated rendering inverse
16. https://clerk.com/docs/references/react/use-auth — `useAuth()` hook (token, signOut, etc.)
17. https://clerk.com/docs/references/react/use-user — `useUser()` hook (profile data)
18. https://clerk.com/docs/customization/overview — theming + appearance

## C. Clerk — backend / token verification

19. https://clerk.com/docs/backend-requests/overview — how server-side auth works
20. https://clerk.com/docs/backend-requests/resources/session-tokens — what's in the JWT
21. https://clerk.com/docs/backend-requests/handling/manual-jwt — verify a Clerk JWT yourself (FastAPI path)
22. https://clerk.com/docs/backend-requests/making/jwt-templates — custom JWT shape for downstream services
23. https://clerk.com/docs/references/backend/overview — backend SDK index
24. https://api.clerk.com/v1 — REST API base
25. https://clerk.com/docs/references/backend-api — REST reference
26. https://github.com/clerk/clerk-sdk-python — official Python SDK (use for FastAPI)

## D. Clerk — Google / OAuth config

27. https://clerk.com/docs/authentication/social-connections/overview — social providers index
28. https://clerk.com/docs/authentication/social-connections/google — Google specifically
29. https://clerk.com/docs/authentication/configuration/sign-up-sign-in-options — what you can toggle
30. https://clerk.com/docs/authentication/configuration/session-options — session length, multi-session, etc.

## E. Clerk ↔ Supabase integration — most important section

31. https://clerk.com/docs/integrations/databases/supabase — official integration guide (Clerk handles auth, Supabase handles data via JWT template + RLS)
32. https://supabase.com/partners/integrations/clerk — Supabase's side of the same integration
33. https://clerk.com/blog/clerk-and-supabase-config-guide — walkthrough blog post
34. https://supabase.com/docs/guides/database/postgres/row-level-security — RLS policies that read Clerk JWT claims
35. https://github.com/clerk/clerk-supabase-starter — reference repo (verify name; community variants also exist)

## F. Supabase — keep using as Postgres

36. https://supabase.com/docs — docs root
37. https://supabase.com/docs/guides/database/overview — DB layer (this is what we keep)
38. https://supabase.com/docs/guides/api — auto-generated REST/GraphQL
39. https://supabase.com/docs/reference/python/introduction — `supabase-py` SDK
40. https://supabase.com/docs/guides/database/connecting-to-postgres — direct psycopg connection (current path)
41. https://supabase.com/docs/guides/database/postgres/jwt — how Supabase reads JWT claims for RLS
42. https://supabase.com/dashboard/project/_/settings/api — where you find URL + anon key
43. https://supabase.com/docs/guides/troubleshooting — when DB connection breaks

## G. FastAPI + cookies + CORS

44. https://fastapi.tiangolo.com/ — docs root
45. https://fastapi.tiangolo.com/tutorial/security/ — auth patterns, including bearer
46. https://fastapi.tiangolo.com/tutorial/cors/ — `CORSMiddleware` setup (need `allow_credentials=True` + specific origin)
47. https://fastapi.tiangolo.com/advanced/middleware/ — custom middleware if Clerk verification is a dep
48. https://www.starlette.io/middleware/ — underlying Starlette middleware (FastAPI is built on it)
49. https://pyjwt.readthedocs.io/en/stable/ — PyJWT (already in use)
50. https://pyjwt.readthedocs.io/en/stable/usage.html#retrieve-rsa-signing-keys-from-a-jwks-endpoint — fetching JWKS (Clerk uses RS256, JWKS-based)

## H. Web platform fundamentals

51. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie — cookie attribute reference
52. https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite — the attribute that bit us in OAuth
53. https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies — full cookie model
54. https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS — CORS spec
55. https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS/Errors — debugging CORS failures
56. https://web.dev/articles/samesite-cookies-explained — SameSite explainer (more readable than the spec)
57. https://web.dev/articles/cross-origin-resource-policy — CORP/COEP if Clerk is embedded in iframes
58. https://owasp.org/www-project-cheat-sheets/cheatsheets/Session_Management_Cheat_Sheet.html — OWASP session hygiene

## I. OAuth / JWT standards

59. https://datatracker.ietf.org/doc/html/rfc6749 — OAuth 2.0 core
60. https://datatracker.ietf.org/doc/html/rfc7636 — PKCE
61. https://datatracker.ietf.org/doc/html/rfc7519 — JWT
62. https://datatracker.ietf.org/doc/html/rfc8725 — JWT best current practices (read this — it's short)
63. https://oauth.net/2/ — informal OAuth landing with curated resources

## J. Vite + React env-var plumbing

64. https://vitejs.dev/guide/env-and-mode.html — `VITE_*` envs (relevant for `VITE_CLERK_PUBLISHABLE_KEY`)
65. https://vitejs.dev/guide/build.html — build args (Dockerfile uses these)
66. https://react.dev/reference/react — React API
67. https://react.dev/learn/you-might-not-need-an-effect — useful when porting auth hooks
68. https://docs.docker.com/compose/environment-variables/envvars/ — Compose env precedence (bit us earlier with `VITE_*` not propagating)

## K. Comparisons / decision context

69. https://clerk.com/blog — engineering blog (good for "why this not that" posts)
70. https://workos.com/blog/best-auth-services-comparison — third-party comparison incl. Clerk, Auth0, WorkOS, Supabase
71. https://supabase.com/blog/clerk-tldraw — sample of Supabase + Clerk in a real product
72. https://news.ycombinator.com/from?site=clerk.com — HN posts about Clerk (skim comments for footguns)
73. https://github.com/clerk/javascript/discussions — official discussion board for real-world issues

---

## Suggested reading order for the next hour

1. **#31** (Clerk-Supabase integration guide) — the architecture decision in one page.
2. **#3** (React quickstart) — get `<ClerkProvider>` + `<SignIn />` rendering.
3. **#21 + #50** (manual JWT verification + JWKS) — wire FastAPI to verify Clerk tokens.
4. **#34 + #41** (RLS + Supabase JWT) — only if browser-direct DB access is wanted; skip if backend-only.
5. **#46** (CORS) — only if the cookie/origin issue resurfaces.

Everything else is reference material for when something specific breaks.
