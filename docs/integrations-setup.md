# Noni — Third-Party Integration Setup

This is the **only** document you need to set up Noni's outside services.
It tells you the **one right way** to do each step. No alternatives, no
"depending on your situation." Just do it in this order.

You will set up **three accounts**:

1. **Supabase** — handles login and stores all our data
2. **Google Cloud** — powers the "Sign in with Google" button
3. **Stripe** — takes credit cards

When you are done, the file `.env` (in the repo root) and `frontend/.env`
will be filled out, and Noni will be ready to deploy.

Allow about **45 minutes** start to finish.

---

## Glossary

Read this once before you begin. Every term used later in the guide is
defined here.

| Term | What it means |
| --- | --- |
| **`.env` file** | A plain-text file in the repo where we store secret values (passwords, keys). It is **never** committed to Git — it lives only on your machine and on the server. |
| **Environment variable** | A named value that `.env` provides to the app, e.g. `STRIPE_SECRET_KEY=sk_test_xyz`. The app reads these at startup. |
| **API key** | A long random string that proves to a service ("Stripe") that requests are coming from us. Treat it like a password. |
| **Secret key vs. publishable key** | Stripe gives you two. The **secret** key (`sk_...`) must stay on the server. The **publishable** key (`pk_...`) is safe to put in the browser. |
| **Webhook** | A message a service sends to *us* when something happens. Example: Stripe POSTs to our backend the moment a customer pays. |
| **Webhook signing secret** | A string the service uses to "sign" each webhook so we can be sure it really came from them, not an attacker. |
| **JWT (JSON Web Token)** | A short string of text that proves "this user is logged in and they are person X." Supabase issues one when a user signs in; our backend checks the signature on every request. |
| **JWT secret** | The shared password between Supabase and our backend that makes JWT signatures verifiable. |
| **OAuth** | The standard way an app says "let me sign in using my existing Google/Apple/etc. account." The user types their password to **Google**, never to us. |
| **OAuth consent screen** | The page Google shows the user the first time they sign in: "Noni would like to access your email address. Allow?" Google requires us to register what our app is called and what we will ask for. |
| **Redirect URI** | The exact URL Google will send the user back to after they approve sign-in. It must match a URL we pre-registered, character for character. |
| **Project URL** (Supabase) | The unique web address Supabase gives our project, e.g. `https://abcd1234.supabase.co`. |
| **Anon key** (Supabase) | A public key the frontend uses to talk to Supabase. Safe to put in the browser. |
| **Service role key** (Supabase) | A super-powerful admin key. **Never** put this in the frontend or commit it. We do not use it in Noni. |
| **Connection string** (Postgres) | The URL the app uses to talk to the database, e.g. `postgresql://user:password@host:5432/dbname`. |
| **Test mode** (Stripe) | A separate sandbox where you can pretend to charge cards without real money moving. All keys start with `sk_test_` or `pk_test_`. |
| **Price ID** (Stripe) | A short code like `price_1Q...` that points to a specific product + amount. Our app sends this code to Stripe to start a checkout. |
| **Stripe CLI** | A command-line tool from Stripe that forwards webhook events from Stripe's servers to your laptop while you develop. |
| **PaaS** | "Platform as a Service" — a hosting company that runs your code without you managing servers. (Render, Fly.io, etc.) |

---

## Before you start

1. Open a terminal in the repo: `cd /mnt/c/Users/kimem/Noni`
2. Make a working copy of the env files:
   ```bash
   cp .env.example .env
   cp frontend/.env.example frontend/.env
   ```
3. Open `.env` and `frontend/.env` in a text editor and keep them open. You
   will paste many values into them as you go.
4. Have an email account ready that you control. You will sign up for three
   services with it.

---

## Part 1 — Supabase

**What it does for Noni:** Supabase gives us two things in one account: a
**login system** (the verified-identity tokens we trust) and a **PostgreSQL
database** (where every user, purchase, and event is stored). Without
Supabase, Noni has no memory and no way to know who is signed in.

### Steps

1. Go to **https://supabase.com**. Click **"Start your project"** in the top
   right. Sign up with GitHub or with an email + password.

2. Once signed in, click **"New project"** (large green button).

3. Fill in the form:
   - **Organization:** leave the default (your personal org).
   - **Project name:** type `noni-staging`.
   - **Database password:** click the **"Generate a password"** link. A
     strong random password appears. Click **Copy** and paste it into a
     password manager or a note. You cannot view it again later.
   - **Region:** choose the region closest to your users. For US-based
     users pick **`East US (North Virginia)`**.
   - **Pricing plan:** **Free**.
   - Click **"Create new project"**.

4. Wait. The page shows a progress spinner for about two minutes while
   Supabase provisions the database. Do not close the tab.

5. When provisioning finishes, the dashboard for your project loads. Now
   collect five values:

   **Value 1 — Project URL**
   - Left sidebar (gear icon at the bottom): **Project Settings** → **API**.
   - Top of the page, under **Project URL**, copy the URL. It looks like
     `https://abcd1234.supabase.co`.
   - Paste it into `.env`:
     ```
     SUPABASE_URL=https://abcd1234.supabase.co
     SUPABASE_JWT_ISSUER=https://abcd1234.supabase.co/auth/v1
     ```
   - Paste it into `frontend/.env`:
     ```
     VITE_SUPABASE_URL=https://abcd1234.supabase.co
     ```

   **Value 2 — Anon (public) key**
   - Same page, under **Project API keys**, find the row labeled
     **`anon` `public`**. Click the eye icon to reveal, then copy.
   - Paste it into `frontend/.env`:
     ```
     VITE_SUPABASE_ANON_KEY=<paste here>
     ```

   **Value 3 — JWT secret**
   - Same page, scroll down to **JWT Settings**. Click the eye next to
     **JWT Secret** and copy the long string.
   - Paste it into `.env`:
     ```
     SUPABASE_JWT_SECRET=<paste here>
     ```

   **Value 4 — Database connection string (pooled)**
   - Left sidebar: **Project Settings** → **Database** → scroll to
     **Connection string** → click the **URI** tab → click the
     **"Transaction pooler"** sub-tab.
   - Copy the URL. It contains the placeholder text `[YOUR-PASSWORD]`.
   - Open the URL in your text editor and **replace `[YOUR-PASSWORD]`**
     with the database password you saved in step 3.
   - Paste the result into `.env`:
     ```
     DATABASE_URL=postgresql://postgres.abcd:YOURPASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
     ```

   **Value 5 — Database connection string (direct)**
   - Same page, click the **"Direct connection"** sub-tab. Copy that URL,
     replace the password placeholder the same way.
   - Paste into `.env`:
     ```
     DATABASE_URL_DIRECT=postgresql://postgres:YOURPASSWORD@db.abcd.supabase.co:5432/postgres
     ```

6. Switch the auth provider on. Open `.env` and change:
   ```
   AUTH_PROVIDER=supabase
   ```
   And in `frontend/.env`:
   ```
   VITE_AUTH_PROVIDER=supabase
   ```

7. **Stop here.** Move on to Part 2. You will return to the Supabase
   dashboard one more time at the end of Part 2.

---

## Part 2 — Google Cloud

**What it does for Noni:** This is the actual machinery behind the "Sign in
with Google" button. Google verifies the user's identity and tells Supabase,
who tells us. Without registering with Google, the button cannot work.

### Steps

1. Go to **https://console.cloud.google.com**. Sign in with the Google
   account that should own these credentials. (A personal Gmail is fine for
   staging; use a work Google account for production later.)

2. **Create a project:**
   - Top bar, click the project picker (it says "Select a project" or shows
     the name of an existing project).
   - In the dialog that opens, click **"NEW PROJECT"** (top right).
   - Project name: `noni`.
   - Location: leave **"No organization"**.
   - Click **CREATE**. Wait ten seconds.
   - Click the project picker again and select **`noni`**.

3. **Configure the OAuth consent screen.** Google requires this before it
   will issue credentials.

   - Left sidebar (the hamburger menu) → **"APIs & Services"** → **"OAuth
     consent screen"**.
   - **User Type:** click **External** → **CREATE**.
   - On the next page fill in:
     - **App name:** `Noni`
     - **User support email:** your email (pick from the dropdown).
     - **App logo:** leave blank.
     - **Application home page:** leave blank.
     - **Application privacy policy link:** leave blank.
     - **Application terms of service link:** leave blank.
     - **Authorized domains:** click **+ ADD DOMAIN**, type `supabase.co`,
       press Enter.
     - **Developer contact information:** your email again.
     - Click **SAVE AND CONTINUE**.
   - On the **Scopes** page, click **ADD OR REMOVE SCOPES**. A side panel
     opens with a long list. Tick the boxes for:
     - `.../auth/userinfo.email`
     - `.../auth/userinfo.profile`
     - `openid`
     - Click **UPDATE** at the bottom of the panel.
     - Click **SAVE AND CONTINUE**.
   - On the **Test users** page, click **+ ADD USERS**, type your email,
     click **ADD**, then **SAVE AND CONTINUE**. (Only emails on this list
     can sign in until the app is published.)
   - On the **Summary** page, click **BACK TO DASHBOARD**.

4. **Create the OAuth client ID:**

   - Left sidebar → **"APIs & Services"** → **"Credentials"**.
   - Top bar, click **"+ CREATE CREDENTIALS"** → choose **"OAuth client ID"**.
   - **Application type:** `Web application`.
   - **Name:** `Noni Supabase`.
   - **Authorized JavaScript origins:** click **+ ADD URI**, type your
     Supabase project URL exactly: `https://abcd1234.supabase.co` (no
     trailing slash). Use the URL you saved in Part 1 step 5.
   - **Authorized redirect URIs:** click **+ ADD URI**, type your Supabase
     project URL **plus** `/auth/v1/callback`:
     `https://abcd1234.supabase.co/auth/v1/callback`.
   - Click **CREATE**.
   - A dialog appears showing **"Your Client ID"** and **"Your Client
     Secret."** Copy **both** values. Keep this dialog open.

5. **Plug them into Supabase:**

   - In a new browser tab, open your Supabase dashboard.
   - Left sidebar → **Authentication** → **Providers**.
   - Scroll down to find **Google** in the provider list. Click it.
   - Toggle **"Enable Sign in with Google"** to ON.
   - **Client ID (for OAuth):** paste the Client ID from step 4.
   - **Client Secret (for OAuth):** paste the Client Secret from step 4.
   - Leave **"Authorized Client IDs"** blank.
   - Click **Save**.

6. You can now close the Google dialog. **Sign in with Google is now
   wired.**

### What you put in `.env` for Google

**Nothing.** Google's credentials live inside Supabase's dashboard. Our
backend never talks to Google directly — it only ever talks to Supabase.

---

## Part 3 — Stripe

**What it does for Noni:** Stripe shows the credit-card form, charges the
card, and tells our backend "person X just paid." Our backend then unlocks
the paid modules for that person. Without Stripe we cannot accept money
without months of compliance work.

### Steps

1. Go to **https://stripe.com**. Click **"Start now"** (top right). Sign up
   with your email and a strong password. Verify your email when Stripe
   sends the link.

2. After signing in you are dropped on the Stripe dashboard. Look at the
   top-right corner for a toggle labeled **"Test mode"** with a colored dot
   next to it. **Make sure Test mode is ON.** Every key you collect from
   here forward must start with `sk_test_` or `pk_test_`.

3. **Get the API keys:**

   - Left sidebar → **Developers** → **API keys**.
   - Under **Standard keys** you will see two rows.
   - Row 1: **Publishable key** — already visible. Click the copy icon.
     Paste into `.env`:
     ```
     STRIPE_PUBLISHABLE_KEY=pk_test_xxx
     ```
   - Row 2: **Secret key** — click **"Reveal test key"**, then click the
     copy icon. Paste into `.env`:
     ```
     STRIPE_SECRET_KEY=sk_test_xxx
     ```

4. **Switch the payment provider on.** In `.env`:
   ```
   PAYMENT_PROVIDER=stripe
   ```

5. **Create the product** (the thing users buy). We have a script that
   does this idempotently — it will create the product the first time and
   do nothing the next times.

   ```bash
   python scripts/seed_products.py
   ```

   The script logs into Stripe with the secret key you just saved, creates
   a product called **"Noni Modules 4–5"** priced at **$24.00 USD
   one-time**, and prints the new **price ID** to your terminal. It looks
   like `price_1Qabc123XYZ`.

   - Copy the price ID and paste into `.env`:
     ```
     STRIPE_PRICE_ID_MODULES_4_5=price_1Qabc123XYZ
     ```

6. **Install the Stripe CLI.** This tool forwards webhook events from
   Stripe's servers to your laptop while you develop. Run:

   ```bash
   curl -fsSL https://packages.stripe.dev/api/security/keypair/stripe-cli-gpg/public \
     | sudo gpg --dearmor -o /usr/share/keyrings/stripe.gpg
   echo "deb [signed-by=/usr/share/keyrings/stripe.gpg] https://packages.stripe.dev/stripe-cli-debian-local stable main" \
     | sudo tee /etc/apt/sources.list.d/stripe.list
   sudo apt update && sudo apt install -y stripe
   stripe login
   ```

   The last command opens a browser. Click **Allow** on the page Stripe
   shows. Return to the terminal — it will print "Done!".

7. **Start the webhook forwarder.** Run this in a terminal that you keep
   open while developing:

   ```bash
   stripe listen --forward-to http://localhost:8000/api/billing/webhook
   ```

   The first line of output looks like:
   ```
   Ready! Your webhook signing secret is whsec_xxx
   ```

   - Copy `whsec_xxx` and paste into `.env`:
     ```
     STRIPE_WEBHOOK_SECRET=whsec_xxx
     ```

   Leave that terminal running. If you close it, webhooks stop arriving.

---

## Part 4 — Final `.env` checklist

Open `.env`. **Every** line below must have a real value to the right of the
`=`. If any line is blank or still says `change-me`, the app will not work.

```
DATABASE_URL=postgresql://...
DATABASE_URL_DIRECT=postgresql://...

AUTH_PROVIDER=supabase
SUPABASE_URL=https://abcd1234.supabase.co
SUPABASE_JWT_SECRET=<long random string>
SUPABASE_JWT_ISSUER=https://abcd1234.supabase.co/auth/v1

PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_ID_MODULES_4_5=price_...

SECRET_KEY=<32 random bytes>
SESSION_SECRET=<32 random bytes, different from SECRET_KEY>
```

Generate the two random secrets with:
```bash
openssl rand -hex 32
```
Run it twice. Paste the first result into `SECRET_KEY` and the second into
`SESSION_SECRET`.

Open `frontend/.env`:

```
VITE_AUTH_PROVIDER=supabase
VITE_SUPABASE_URL=https://abcd1234.supabase.co
VITE_SUPABASE_ANON_KEY=<anon public key>
```

---

## Part 5 — End-to-end smoke test

Run these in three separate terminals.

**Terminal 1 — start the stack:**
```bash
docker compose up -d
docker compose logs -f api
```

**Terminal 2 — start the Stripe webhook forwarder:**
```bash
stripe listen --forward-to http://localhost:8000/api/billing/webhook
```

**Terminal 3 — your normal terminal.** In a browser, open
`http://localhost:8080`.

Now do, in order:

1. Click **Sign in**. You are redirected to a real Google sign-in page.
   Sign in with the email you added to Google's "Test users" list.
2. After signing in you land back on Noni, signed in.
3. Navigate until you hit a paywalled module. Click **Buy modules 4–5**.
4. You are redirected to Stripe's hosted checkout page.
5. Enter test card details: card number `4242 4242 4242 4242`, any future
   expiry, any 3-digit CVC, any 5-digit ZIP. Click **Pay**.
6. You land on the success page. Click **Continue**.
7. The previously paywalled content now loads.

**Watch Terminal 1.** When step 5 completes, you should see a log line like:
```
INFO  webhook accepted event=checkout.session.completed
```
And in Terminal 2:
```
checkout.session.completed [evt_xxx] -> 200 OK
```

If both appear, every integration is working end-to-end.

---

## Part 6 — Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `connection refused` to database | Supabase password wrong, or `[YOUR-PASSWORD]` placeholder not replaced. | Re-copy the connection string and edit the password by hand. |
| Sign-in redirects to Google then errors `redirect_uri_mismatch` | The redirect URI in Google Cloud does not exactly match Supabase's callback URL. | In Google Cloud → Credentials → your OAuth client, add `https://<your-project>.supabase.co/auth/v1/callback` exactly. |
| Sign-in works in Google but Supabase shows "Email not confirmed" | Your email is not on the OAuth consent screen's Test Users list. | Add it under Google Cloud → OAuth consent screen → Test users. |
| Stripe checkout opens but says "Invalid price" | `STRIPE_PRICE_ID_MODULES_4_5` is wrong or empty. | Re-run `python scripts/seed_products.py` and copy the printed price ID. |
| Payment succeeds but content stays locked | Webhook not reaching the backend (Terminal 2 shows nothing). | Make sure `stripe listen` is running and `STRIPE_WEBHOOK_SECRET` matches the value `stripe listen` printed. |
| `JWT signature invalid` in backend logs | `SUPABASE_JWT_SECRET` was copied incorrectly. | Re-copy from Supabase → Settings → API → JWT Settings → JWT Secret. Restart the backend. |

---

## Part 7 — Where each integration lives in the code (reference)

You should not need to edit these files for setup, but if you are curious:

| Integration | Code path |
| --- | --- |
| Supabase auth (JWT verify) | `backend/services/auth_provider.py` |
| Supabase OAuth redirect (frontend) | `frontend/src/api/oauth.ts` |
| Postgres connection | `backend/core/database.py` |
| Stripe checkout + webhook | `backend/services/payment_provider.py`, `backend/api/routes/billing.py` |
| Stripe product seeding | `scripts/seed_products.py` |

That is everything. After Part 5 passes, Noni is fully wired to its
third-party services and ready for staging deployment (see
`docs/staging-deploy.md`).
