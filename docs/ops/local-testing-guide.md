# Local Testing Guide for EPIC-002 Changes

**Purpose:** Test EPIC-002 login loop fix and onboarding flow locally  
**Created:** 2026-08-09  
**Prerequisites:** Python, Node.js, Clerk account  

---

## Overview

This guide will help you test the EPIC-002 changes locally to verify the login loop fix and onboarding flow work correctly before deploying to production.

---

## Prerequisites

### Required Accounts

1. **Clerk Account** (Free tier works)
   - Sign up at https://clerk.com
   - Create a new application called "Mynaani Local Testing"
   - Note your API keys (Publishable Key and Secret Key)

### Required Software

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use Docker)
- Git

---

## Step 1: Setup Clerk Configuration

### 1.1 Create Clerk Application

1. Go to https://dashboard.clerk.com
2. Click "Create Application"
3. Name it "Mynaani Local Testing"
4. Select "Email" and "Password" authentication
5. Note your API keys:
   - **Publishable Key**: Starts with `pk_test_...`
   - **Secret Key**: Starts with `sk_test_...`

### 1.2 Configure Clerk Redirect URLs

1. In Clerk dashboard, go to "Domains"
2. Add allowed redirect URLs:
   - `http://localhost:5173/*`
   - `http://localhost:8000/*`
3. Configure "After sign-in URL": `http://localhost:5173/welcome`
4. Configure "After sign-up URL": `http://localhost:5173/welcome`

---

## Step 2: Setup Environment Variables

### 2.1 Backend Environment Configuration

Update `.env` file in the root directory:

```bash
# Update the Clerk keys with your actual keys
AUTH_PROVIDER=clerk
CLERK_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_CLERK_PUBLISHABLE_KEY
CLERK_SECRET_KEY=sk_test_YOUR_ACTUAL_CLERK_SECRET_KEY
```

### 2.2 Frontend Environment Configuration

Update `frontend/.env` file:

```bash
# Update the Clerk key with your actual key
VITE_AUTH_PROVIDER=clerk
VITE_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_CLERK_PUBLISHABLE_KEY
```

---

## Step 3: Setup Database

### Option A: Use Docker (Recommended)

```bash
# Start PostgreSQL using Docker
docker-compose up -d db

# Wait for database to start (10-15 seconds)
```

### Option B: Use Local PostgreSQL

```bash
# Start PostgreSQL service
# On Windows (using pgAdmin or service)
# On Mac/Linux: sudo service postgresql start

# Create database
createdb noni
```

### Run Database Migration

```bash
# Apply database schema and EPIC-002 migration
cd backend
alembic upgrade head

# Verify migration
alembic current
# Should show: epic002_account_preferences
```

---

## Step 4: Start Backend Server

```bash
# Open terminal in backend directory
cd backend

# Install Python dependencies (if not already installed)
pip install -r ../requirements.txt

# Start the backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

**Verify Backend:**
```bash
# In another terminal, test health endpoint
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

---

## Step 5: Start Frontend Server

```bash
# Open new terminal in frontend directory
cd frontend

# Install Node dependencies (if not already installed)
npm install

# Start the frontend development server
npm run dev
```

**Expected Output:**
```
  VITE v5.4.10  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Step 6: Test Login Loop Fix

### 6.1 Access Application

1. Open browser to: `http://localhost:5173`
2. You should see the landing page

### 6.2 Test Authentication Flow

1. Click "Sign In" button
2. Sign up for a new account using Clerk (email + password)
3. **CRITICAL TEST:** After sign-in, you should be redirected to `/welcome`
4. **SUCCESS:** If you see the Welcome page, the login loop is fixed!
5. **FAILURE:** If you see a login loop, the fix is not working

### 6.3 Expected Flow After Fix

1. **Sign In → Welcome Page:** User redirected to `/welcome`
2. **Welcome → Account Setup:** Click "Get Started" to go to `/setup`
3. **Account Setup → Getting Started:** Complete profile to go to `/getting-started`
4. **Getting Started → Curriculum:** Complete onboarding to access curriculum

---

## Step 7: Test Onboarding Flow

### 7.1 Welcome Page Test

- [ ] Welcome page loads without errors
- [ ] Display shows "Welcome to Mynaani"
- [ ] "Get Started" button is visible
- [ ] "Maybe later" option is available

### 7.2 Account Setup Page Test

- [ ] Account setup page loads
- [ ] Display name field is present
- [ ] Learning preferences are shown
- [ ] Form submission works
- [ ] Success message appears
- [ ] Auto-redirects to getting-started after 2 seconds

### 7.3 Getting Started Page Test

- [ ] Getting started page loads
- [ ] Progress indicators are visible
- [ ] Step-by-step guidance works
- [ ] Completion celebration appears
- [ ] Redirects to curriculum after completion

---

## Step 8: Troubleshooting

### Issue: Backend won't start

**Solution:**
```bash
# Check if database is running
docker-compose ps

# Check database connection
# Verify DATABASE_URL in .env is correct

# Check port 8000 is not in use
netstat -ano | findstr :8000
```

### Issue: Frontend won't start

**Solution:**
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules
npm install

# Check port 5173 is not in use
netstat -ano | findstr :5173
```

### Issue: Clerk authentication fails

**Solution:**
```bash
# Verify Clerk keys are correct in both .env files
# Check Clerk dashboard for redirect URLs
# Ensure http://localhost:5173 is in allowed origins
```

### Issue: Login loop still occurs

**Solution:**
```bash
# Check browser console for errors
# Verify Clerk redirect URLs are configured correctly
# Check that afterSignInUrl is set to /welcome
# Clear browser cookies and cache
```

### Issue: Database migration fails

**Solution:**
```bash
# Check database connection
# Verify DATABASE_URL is correct
# Check database exists
psql postgresql://postgres:postgres@localhost:5432/noni
```

---

## Step 9: Verification Checklist

### Authentication Flow
- [ ] User can sign up successfully
- [ ] User is redirected to `/welcome` (NOT login loop)
- [ ] User can sign in successfully
- [ ] Session persists across page refreshes

### Onboarding Flow
- [ ] Welcome page displays correctly
- [ ] Account setup form works
- [ ] Getting started page works
- [ ] User can access curriculum after onboarding

### Technical Verification
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] Database migration applied successfully
- [ ] No console errors in browser
- [ ] No backend errors in terminal

---

## Step 10: Clean Up

```bash
# Stop servers (Ctrl+C in each terminal)

# Stop database (if using Docker)
docker-compose down

# Remove test data from database (optional)
alembic downgrade epic002_account_preferences
alembic upgrade head
```

---

## Next Steps After Local Testing

If local testing is successful:

1. **Deploy to Staging:** Follow the GitHub Staging Environment Setup Guide
2. **Configure Clerk for Staging:** Update Clerk dashboard with staging URLs
3. **Test in Staging:** Complete staging testing checklist
4. **Deploy to Production:** After staging approval, deploy to production

---

## Important Notes

1. **Clerk Keys Required:** You MUST have actual Clerk API keys to test the login loop fix
2. **Database Required:** The changes require a database to work properly
3. **Both Servers Needed:** Both backend and frontend must be running
4. **Redirect URLs Critical:** Clerk redirect URLs must be configured correctly

---

**Guide Created:** 2026-08-09  
**EPIC-002 Version:** 1.0  
**Status:** Ready for Local Testing