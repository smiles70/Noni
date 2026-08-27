# GitHub Staging Environment Setup Guide

**Guide Version:** 1.0  
**Created:** 2026-08-09  
**Purpose:** Step-by-step instructions for creating a staging environment using GitHub  
**Target Audience:** DevOps Engineers, SRE Team, Development Team  

---

## Overview

This guide provides comprehensive instructions for setting up a staging environment for the Mynaani project using GitHub. The staging environment will mirror production configuration and allow for safe testing of changes before production deployment.

**Key Benefits:**
- Safe testing environment separate from production
- Automated deployment workflows
- Configuration parity with production
- Rollback capability
- Isolated testing of database migrations

---

## Prerequisites

### Required Accounts and Access

1. **GitHub Account**
   - Admin access to the Mynaani repository
   - Ability to create branches and workflows
   - Access to GitHub Actions

2. **Cloudflare Pages Account**
   - Access to Mynaani frontend project
   - Ability to create projects
   - Access to environment variables

3. **Fly.io Account**
   - Access to Mynaani backend apps
   - Ability to create apps
   - Access to environment variables
   - API token for automation

4. **Clerk Account**
   - Access to Mynaani Clerk application
   - Ability to configure redirect URLs
   - Access to API keys

5. **BetterStack Account** (Optional)
   - Access to BetterStack dashboard
   - Ability to create monitoring sources
   - Access to API keys

### Required Tools

- Git command-line tools
- GitHub CLI (gh) - recommended
- Fly.io CLI (flyctl)
- Node.js and npm (for frontend builds)
- Python (for backend)
- PostgreSQL client (for database management)

---

## Step 1: GitHub Repository Setup

### 1.1 Create Staging Branch

**Objective:** Create a dedicated branch for staging deployments

```bash
# Create staging branch from main
git checkout -b staging

# Push to GitHub
git push -u origin staging
```

### 1.2 Configure Branch Protection

**Objective:** Protect the staging branch to ensure stability

1. Navigate to GitHub repository settings
2. Go to "Branches" → "Branch protection rules"
3. Add rule for `staging` branch:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date
   - ✅ Do not allow bypassing settings

### 1.3 Create Environment in GitHub

**Objective:** Create staging environment for GitHub Actions

1. Navigate to repository settings
2. Go to "Environments" → "New environment"
3. Create environment named `staging`
4. Configure environment rules:
   - ✅ Require manual approval
   - ✅ Add required reviewers (Tech Lead, SRE Lead)
   - ✅ Add wait timer (recommended: 5 minutes)

---

## Step 2: GitHub Actions Workflow Configuration

### 2.1 Create Staging Deployment Workflow

**Objective:** Automate deployment to staging environment

Create `.github/workflows/deploy-staging.yml`:

```yaml
name: Deploy to Staging

on:
  push:
    branches:
      - staging
  workflow_dispatch:

jobs:
  deploy-backend:
    name: Deploy Backend to Staging
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run database migration
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          cd backend
          alembic upgrade head

      - name: Deploy to Fly.io Staging
        uses: superfly/flyctl-actions@master
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        with:
          args: "deploy --app noni-api-staging --remote staging"

  deploy-frontend:
    name: Deploy Frontend to Staging
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Build frontend
        env:
          VITE_AUTH_PROVIDER: ${{ secrets.STAGING_AUTH_PROVIDER }}
          VITE_CLERK_PUBLISHABLE_KEY: ${{ secrets.STAGING_CLERK_PUBLISHABLE_KEY }}
        run: |
          cd frontend
          npm run build

      - name: Deploy to Cloudflare Pages Staging
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy frontend/dist --project-name=noni-web-staging

  run-tests:
    name: Run Integration Tests
    runs-on: ubuntu-latest
    needs: [deploy-backend, deploy-frontend]
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        env:
          DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL }}
        run: |
          cd backend
          pytest tests/ -v

      - name: Run frontend tests
        run: |
          cd frontend
          npm test
```

### 2.2 Configure GitHub Secrets

**Objective:** Add staging environment secrets to GitHub

Navigate to repository settings → "Secrets and variables" → "Actions" → "New repository secret"

**Required Secrets:**

1. **Database Configuration:**
   - `STAGING_DATABASE_URL` - Staging database connection string
   - `STAGING_DATABASE_USER` - Database username
   - `STAGING_DATABASE_PASSWORD` - Database password

2. **Authentication Configuration:**
   - `STAGING_AUTH_PROVIDER` - "clerk" for staging
   - `STAGING_CLERK_PUBLISHABLE_KEY` - Clerk publishable key for staging
   - `STAGING_CLERK_SECRET_KEY` - Clerk secret key for staging

3. **Infrastructure Configuration:**
   - `FLY_API_TOKEN` - Fly.io API token
   - `CLOUDFLARE_API_TOKEN` - Cloudflare API token

4. **Monitoring Configuration:**
   - `STAGING_BETTERSTACK_API_KEY` - BetterStack API key (optional)
   - `STAGING_BETTERSTACK_SOURCE_NAME` - "noni-staging"

---

## Step 3: Fly.io Staging App Setup

### 3.1 Create Staging Backend App

**Objective:** Create separate Fly.io app for staging backend

```bash
# Create staging app
flyctl apps create noni-api-staging --org personal

# Add environment variables
flyctl secrets set DATABASE_URL="postgresql://user:password@host:port/dbname" --app noni-api-staging
flyctl secrets set AUTH_PROVIDER="clerk" --app noni-api-staging
flyctl secrets set CLERK_PUBLISHABLE_KEY="pk_test_..." --app noni-api-staging
flyctl secrets set CLERK_SECRET_KEY="sk_test_..." --app noni-api-staging
flyctl secrets set SECRET_KEY="staging-secret-key-min-32-chars" --app noni-api-staging
flyctl secrets set SESSION_SECRET="staging-session-secret-min-32-chars" --app noni-api-staging
```

### 3.2 Configure Staging App

**Objective:** Configure staging app settings

```bash
# Set staging environment
flyctl config set ENVIRONMENT="staging" --app noni-api-staging

# Configure regions (match production or use separate region)
flyctl regions set iad --app noni-api-staging

# Configure scaling (use minimal for staging)
flyctl scale count 1 --app noni-api-staging
```

### 3.3 Create Staging Database

**Objective:** Create separate database for staging

```bash
# Create PostgreSQL database for staging
flyctl postgres create --name noni-db-staging --region iad

# Get connection string
flyctl postgres connect noni-db-staging

# Set DATABASE_URL secret
flyctl secrets set DATABASE_URL="postgresql://..." --app noni-api-staging
```

---

## Step 4: Cloudflare Pages Staging Setup

### 4.1 Create Staging Frontend Project

**Objective:** Create separate Cloudflare Pages project for staging

1. Navigate to Cloudflare Pages dashboard
2. Click "Create a project"
3. Connect to GitHub repository
4. Select repository: `noni`
5. Build configuration:
   - Build command: `cd frontend && npm run build`
   - Build output directory: `frontend/dist`
   - Root directory: `/`
6. Project name: `noni-web-staging`

### 4.2 Configure Staging Environment Variables

**Objective:** Add staging environment variables to Cloudflare Pages

Navigate to project settings → "Environment variables"

**Required Variables:**
- `VITE_AUTH_PROVIDER` = "clerk"
- `VITE_CLERK_PUBLISHABLE_KEY` = "pk_test_..." (staging key)
- `VITE_API_BASE_URL` = "https://noni-api-staging.fly.dev"

### 4.3 Configure Staging Branch

**Objective:** Configure deployment from staging branch

1. Navigate to project settings → "Builds & deployments"
2. Add production branch: `staging`
3. Configure automatic deployments: ✅ Enabled
4. Configure preview deployments: ✅ Disabled (for staging only)

---

## Step 5: Clerk Staging Configuration

### 5.1 Create Staging Clerk Application

**Objective:** Create separate Clerk application for staging

1. Navigate to Clerk dashboard
2. Create new application: "Mynaani Staging"
3. Note the API keys:
   - Publishable key: `pk_test_...`
   - Secret key: `sk_test_...`

### 5.2 Configure Staging Redirect URLs

**Objective:** Configure redirect URLs for staging environment

1. Navigate to Clerk application settings
2. Configure "Allowed redirect URLs":
   - `https://noni-web-staging.pages.dev/*`
   - `https://noni-api-staging.fly.dev/*`

3. Configure "Domain":
   - Add staging domain: `https://noni-web-staging.pages.dev`

4. Configure "After sign-in URL":
   - Set to: `https://noni-web-staging.pages.dev/welcome`

5. Configure "After sign-up URL":
   - Set to: `https://noni-web-staging.pages.dev/welcome`

### 5.3 Configure Email Settings

**Objective:** Configure email for staging (optional)

1. Configure test email server or use Clerk's development emails
2. Configure email templates for staging (prefixed with "[STAGING]")

---

## Step 6: BetterStack Staging Setup (Optional)

### 6.1 Create Staging Monitoring Source

**Objective:** Create separate BetterStack source for staging

1. Navigate to BetterStack dashboard
2. Create new source: "Mynaani Staging"
3. Configure source type: "Application"
4. Note the API key

### 6.2 Configure Staging Environment Variables

**Objective:** Add BetterStack configuration to staging

```bash
# Add to Fly.io secrets
flyctl secrets set BETTERSTACK_API_KEY="staging-api-key" --app noni-api-staging
flyctl secrets set BETTERSTACK_ONBOARDING_SOURCE_NAME="noni-staging" --app noni-api-staging
```

### 6.3 Configure Staging Monitors

**Objective:** Create staging-specific uptime monitors

1. Create uptime monitors for staging endpoints:
   - `https://noni-api-staging.fly.dev/health`
   - `https://noni-web-staging.pages.dev`
   - `https://noni-api-staging.fly.dev/api/v1/auth/config`

2. Configure alert rules for staging (lower thresholds than production)

---

## Step 7: Database Migration Testing

### 7.1 Test Migration in Staging

**Objective:** Verify database migration works in staging

```bash
# Connect to staging database
flyctl postgres connect noni-db-staging

# Run migration in staging
cd backend
DATABASE_URL="postgresql://..." alembic upgrade head

# Verify migration
alembic current
# Should show: epic002_account_preferences
```

### 7.2 Rollback Migration Test

**Objective:** Verify migration rollback works

```bash
# Rollback migration
alembic downgrade epic002_account_preferences

# Verify rollback
alembic current
# Should show: m1_login_schema

# Re-apply migration
alembic upgrade head
```

---

## Step 8: Staging Deployment Workflow

### 8.1 Deploy to Staging

**Objective:** Deploy EPIC-002 to staging environment

```bash
# Merge to staging branch
git checkout main
git pull origin main
git checkout staging
git merge main
git push origin staging
```

### 8.2 Monitor Deployment

**Objective:** Monitor GitHub Actions deployment

1. Navigate to GitHub Actions tab
2. Monitor `deploy-staging` workflow
3. Verify all jobs complete successfully
4. Check for any errors or warnings

### 8.3 Verify Staging Deployment

**Objective:** Verify staging environment is working

**Backend Verification:**
```bash
# Check backend health
curl https://noni-api-staging.fly.dev/health

# Check auth config
curl https://noni-api-staging.fly.dev/api/v1/auth/config

# Check session endpoint (with valid token)
curl -H "Authorization: Bearer <token>" https://noni-api-staging.fly.dev/api/v1/auth/session
```

**Frontend Verification:**
1. Navigate to `https://noni-web-staging.pages.dev`
2. Test authentication flow
3. Verify no login loop
4. Test account setup flow
5. Test onboarding flow

---

## Step 9: Staging Testing Checklist

### 9.1 Authentication Flow Testing

- [ ] User can sign in without login loop
- [ ] User is redirected to `/welcome` after authentication
- [ ] User can complete account setup
- [ ] User can progress through onboarding
- [ ] User can access curriculum after onboarding

### 9.2 Backend API Testing

- [ ] Health endpoint responds correctly
- [ ] Auth config endpoint returns correct provider
- [ ] Session endpoint works with valid token
- [ ] Profile update endpoint works
- [ ] Onboarding status endpoint works
- [ ] Session validation endpoint works

### 9.3 Frontend UI Testing

- [ ] WelcomePage loads correctly
- [ ] AccountSetupPage works correctly
- [ ] GettingStartedPage works correctly
- [ ] All components are geragogy-compliant
- [ ] No console errors
- [ ] Responsive design works

### 9.4 Database Testing

- [ ] Database migration applied correctly
- [ ] Preferences column exists in accounts table
- [ ] Can update user profile
- [ ] Can read onboarding status
- [ ] Data integrity maintained

### 9.5 Integration Testing

- [ ] Complete onboarding flow works end-to-end
- [ ] Telemetry tracking works
- [ ] Error handling works
- [ ] Session validation works
- [ ] BetterStack integration works (if configured)

---

## Step 10: Staging to Production Promotion

### 10.1 Staging Approval Process

**Objective:** Define approval process for promoting to production

1. Complete all testing checklists
2. Get approval from:
   - Tech Lead
   - SRE Lead
   - Product Manager
3. Document staging test results
4. Create promotion ticket

### 10.2 Production Deployment

**Objective:** Deploy to production after staging approval

```bash
# Merge staging to main
git checkout main
git pull origin main
git merge staging
git push origin main
```

### 10.3 Production Verification

**Objective:** Verify production deployment

- [ ] Monitor production deployment workflow
- [ ] Test production authentication flow
- [ ] Test production onboarding flow
- [ ] Monitor production metrics
- [ ] Verify BetterStack monitoring

---

## Troubleshooting

### Common Issues and Solutions

**Issue 1: GitHub Actions Fails**
- **Solution:** Check workflow logs, verify secrets are correctly configured, check API token permissions

**Issue 2: Database Migration Fails**
- **Solution:** Verify DATABASE_URL is correct, check database connectivity, check migration script

**Issue 3: Frontend Build Fails**
- **Solution:** Check Node.js version, verify environment variables, check build logs

**Issue 4: Clerk Authentication Fails**
- **Solution:** Verify Clerk API keys, check redirect URLs, verify application configuration

**Issue 5: Fly.io Deployment Fails**
- **Solution:** Check API token, verify app configuration, check region availability

---

## Maintenance

### Regular Maintenance Tasks

**Weekly:**
- Check staging environment health
- Review staging deployment logs
- Update staging dependencies if needed

**Monthly:**
- Review and rotate staging secrets
- Update staging database with production schema changes
- Review staging monitoring configuration

**Quarterly:**
- Review staging environment configuration
- Update staging documentation
- Clean up old staging data

---

## Security Considerations

### Staging Security Best Practices

1. **Secrets Management:**
   - Never use production secrets in staging
   - Rotate staging secrets regularly
   - Use different API keys for staging

2. **Access Control:**
   - Limit access to staging environment
   - Use separate authentication for staging
   - Implement IP restrictions if needed

3. **Data Protection:**
   - Use test data only (no real user data)
   - Anonymize any production data used for testing
   - Regularly clean staging database

4. **Network Security:**
   - Use secure connections (HTTPS)
   - Implement proper CORS configuration
   - Keep staging isolated from production networks

---

## Cost Optimization

### Staging Cost Reduction

1. **Fly.io:**
   - Use minimal VM size
   - Scale down when not in use
   - Use shared databases instead of dedicated

2. **Cloudflare Pages:**
   - Use free tier for staging
   - Limit build frequency
   - Use preview deployments for testing

3. **Monitoring:**
   - Use minimal monitoring for staging
   - Set longer check intervals
   - Limit alert frequency

---

## Appendix: Quick Reference Commands

### GitHub Commands
```bash
# Create staging branch
git checkout -b staging
git push -u origin staging

# Merge main to staging
git checkout staging
git merge main
git push origin staging
```

### Fly.io Commands
```bash
# Create staging app
flyctl apps create noni-api-staging

# Set secrets
flyctl secrets set DATABASE_URL="..." --app noni-api-staging

# Deploy to staging
flyctl deploy --app noni-api-staging

# Check app status
flyctl status --app noni-api-staging
```

### Database Commands
```bash
# Create staging database
flyctl postgres create --name noni-db-staging

# Connect to staging database
flyctl postgres connect noni-db-staging

# Run migration
alembic upgrade head

# Rollback migration
alembic downgrade epic002_account_preferences
```

---

**Guide Created:** 2026-08-09  
**Guide Version:** 1.0  
**Next Review Date:** After first staging deployment