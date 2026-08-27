# WI-003: EPIC-002 Onboarding Flow Testing Instructions

**Status:** READY FOR USER EXECUTION  
**Dependencies:** WI-001 (completed), WI-002 (completed)  
**Estimated Time:** 30 minutes  
**Requirements:** Database setup, backend server, frontend server  

---

## Pre-Testing Requirements

### 1. Database Setup
```bash
# Option A: Use Docker (recommended)
docker-compose up -d db

# Option B: Use local PostgreSQL
createdb noni

# Run database migration
cd backend
alembic upgrade head
```

### 2. Backend Server Startup
```bash
# Open terminal in backend directory
cd backend

# Install dependencies if needed
pip install -r ../requirements.txt

# Start backend server
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### 3. Frontend Server Startup
```bash
# Open new terminal in frontend directory
cd frontend

# Install dependencies if needed
npm install

# Start frontend server
npm run dev
```

**Expected Output:**
```
  VITE v5.4.10  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## Testing Procedure

### Test 1: Backend Health Check
```bash
# In new terminal
curl http://localhost:8000/health

# Expected: {"status":"healthy"}
```

### Test 2: Authentication Config Check
```bash
curl http://localhost:8000/api/v1/auth/config

# Expected: {"provider":"mock"}
```

### Test 3: Welcome Page Load
1. Open browser to `http://localhost:5173`
2. Should see landing page
3. Click "Sign In" button
4. Should see mock authentication form (email input)
5. Enter any email (e.g., `test@example.com`)
6. Click "Sign In"

**Expected Result:**
- Redirected to `/welcome` page
- Welcome page displays correctly
- No login loop occurs

### Test 4: Account Setup Flow
1. On Welcome page, click "Get Started"
2. Should navigate to `/setup`
3. AccountSetupPage should load
4. Fill in display name and preferences
5. Click "Continue"

**Expected Result:**
- Form submission succeeds
- Success message appears
- Auto-redirects to `/getting-started` after 2 seconds

### Test 5: Getting Started Flow
1. On GettingStartedPage, view step-by-step guidance
2. Click "Next" to progress through steps
3. Complete all steps
4. View completion celebration

**Expected Result:**
- Step progression works
- Completion celebration appears
- Auto-redirects to curriculum after 3 seconds

---

## Verification Checklist

### Authentication Flow
- [ ] Mock authentication form appears
- [ ] User can sign in with any email
- [ ] User redirected to `/welcome` (no login loop)
- [ ] Session persists across page refreshes

### Onboarding Flow
- [ ] WelcomePage loads without errors
- [ ] AccountSetupPage loads and functions
- [ ] GettingStartedPage loads and functions
- [ ] User can progress through onboarding
- [ ] Final redirect to curriculum works

### Technical Verification
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] No console errors in browser
- [ ] No backend errors in terminal
- [ ] Mock provider confirmed in auth config

---

## Troubleshooting

### Issue: Backend won't start
```bash
# Check database connection
docker-compose ps

# Verify DATABASE_URL in .env
# Check port 8000 availability
netstat -ano | findstr :8000
```

### Issue: Frontend won't start
```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules
npm install

# Check port 5173 availability
netstat -ano | findstr :5173
```

### Issue: Login loop still occurs
```bash
# Verify AUTH_PROVIDER=mock in .env
# Verify VITE_AUTH_PROVIDER=mock in frontend/.env
# Clear browser localStorage
# Clear browser cookies and cache
```

### Issue: Mock authentication not working
```bash
# Check browser console for errors
# Verify localStorage has "noni.mock_token"
# Check backend logs for authentication errors
```

---

## Success Criteria

✅ **All Tests Pass:**
- Mock authentication works
- No login loop occurs
- EPIC-002 onboarding flow functional
- All UI components load correctly
- No console or backend errors

⚠️ **Partial Success:**
- Some components work
- Minor errors that don't block functionality
- Document issues for resolution

❌ **Failure:**
- Critical components fail
- Login loop still occurs
- Cannot progress through onboarding
- Requires code modifications

---

## Next Steps After Testing

### If Testing Successful:
1. Proceed to WI-004: Security Guard Implementation
2. Implement WI-005: Documentation Updates
3. Plan WI-006: Long-term Auth Provider Evaluation

### If Testing Fails:
1. Document specific failures
2. Identify root cause
3. Implement fixes
4. Re-test until successful

---

**WI-003 Status:** READY FOR USER EXECUTION  
**Required Action:** User needs to start servers and execute testing  
**Estimated Completion Time:** 30 minutes