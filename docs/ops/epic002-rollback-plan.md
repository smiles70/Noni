# EPIC-002 Rollback Plan

**Epic ID:** EPIC-002  
**Epic Name:** Login Loop Fix and Account Setup Flow  
**Deployment Date:** 2026-08-09  
**Rollback Plan Version:** 1.0  
**Status:** READY FOR DEPLOYMENT  

---

## Executive Summary

This document provides step-by-step rollback procedures for EPIC-002 deployment. If any issues arise during or after deployment, this plan ensures quick and safe restoration to the previous stable state.

**Rollback Priority:** MEDIUM - The changes are significant but not critical infrastructure changes  
**Rollback Time:** < 15 minutes  
**Rollback Complexity:** LOW - All changes are backward compatible

---

## Pre-Deployment Rollback Preparation

### Backup Current State

**Git Commit Reference:**
- Current stable commit: [Capture before deployment]
- EPIC-002 commit: `6559222` (deployment commit)

**Database Backup:**
- Export current database schema before migration
- ```bash
  # Backup command (adapt for your database)
  pg_dump noni_production > backup_before_epic002_$(date +%Y%m%d_%H%M%S).sql
  ```

**Environment Configuration Backup:**
- Copy current `.env` file: `.env.backup_epic002`
- Document current Clerk dashboard configuration
- Document current BetterStack configuration (if configured)

---

## Rollback Scenarios

### Scenario 1: Database Migration Failure

**Symptoms:**
- Migration command fails
- Database schema changes not applied
- Application cannot start due to schema mismatch

**Rollback Steps:**

1. **Stop Application:**
   ```bash
   # Stop backend
   railway apps stop noni-api
   
   # Stop frontend (if separate)
   railway apps stop noni-web
   ```

2. **Rollback Database Migration:**
   ```bash
   cd backend
   alembic downgrade epic002_account_preferences
   ```

3. **Verify Schema:**
   ```bash
   alembic current
   # Should show previous migration (m1_login_schema)
   ```

4. **Restart Application:**
   ```bash
   railway apps start noni-api
   railway apps start noni-web
   ```

5. **Verify Functionality:**
   - Test authentication flow
   - Verify no login loop exists
   - Test existing functionality

**Estimated Time:** 5 minutes

---

### Scenario 2: Frontend Deployment Issues

**Symptoms:**
- Frontend build fails
- Frontend deployment fails
- UI errors or broken functionality
- Login loop still present

**Rollback Steps:**

1. **Revert Frontend Changes:**
   ```bash
   git revert 6559222
   ```

2. **Force Frontend Deployment:**
   ```bash
   # For Cloudflare Pages
   wrangler pages deploy frontend/dist --project-name=noni-web
   
   # Or trigger rebuild via Cloudflare dashboard
   ```

3. **Verify Functionality:**
   - Test authentication flow
   - Verify UI loads correctly
   - Test existing functionality

**Estimated Time:** 8 minutes

---

### Scenario 3: Backend Deployment Issues

**Symptoms:**
- Backend deployment fails
- API endpoints return errors
- Authentication not working
- Onboarding endpoints failing

**Rollback Steps:**

1. **Revert Backend Changes:**
   ```bash
   git revert 6559222
   ```

2. **Rollback Database Migration:**
   ```bash
   cd backend
   alembic downgrade epic002_account_preferences
   ```

3. **Redeploy Backend:**
   ```bash
   railway deploy
   ```

4. **Verify Functionality:**
   - Test authentication flow
   - Test API endpoints
   - Verify existing functionality

**Estimated Time:** 10 minutes

---

### Scenario 4: Clerk Dashboard Configuration Issues

**Symptoms:**
- Login loop persists after deployment
- Clerk redirect URLs not working
- Authentication flow broken

**Rollback Steps:**

1. **Revert Clerk Dashboard Changes:**
   - Restore original redirect URLs in Clerk dashboard
   - Original `signInUrl`: (document from pre-deployment state)
   - Original `afterSignInUrl`: (document from pre-deployment state)

2. **Revert Code Changes:**
   ```bash
   git revert 6559222
   ```

3. **Redeploy Application:**
   ```bash
   railway deploy
   ```

4. **Verify Functionality:**
   - Test authentication flow
   - Verify no login loop
   - Test existing functionality

**Estimated Time:** 12 minutes

---

### Scenario 5: Complete Deployment Failure

**Symptoms:**
- Multiple deployment issues
- Application not accessible
- Critical functionality broken

**Rollback Steps:**

1. **Stop All Services:**
   ```bash
   railway apps stop noni-api
   railway apps stop noni-web
   ```

2. **Complete Code Rollback:**
   ```bash
   git revert 6559222
   ```

3. **Complete Database Rollback:**
   ```bash
   cd backend
   alembic downgrade epic002_account_preferences
   ```

4. **Restore Configuration:**
   ```bash
   cp .env.backup_epic002 .env
   ```

5. **Redeploy Everything:**
   ```bash
   railway deploy
   ```

6. **Verify Functionality:**
   - Test authentication flow
   - Test all major functionality
   - Verify application stability

**Estimated Time:** 15 minutes

---

## Post-Rollback Verification

### Critical Functionality Checklist

After any rollback, verify the following:

- [ ] Application starts successfully
- [ ] Authentication flow works (no login loop)
- [ ] Users can sign in and access curriculum
- [ ] Database queries work correctly
- [ ] API endpoints respond correctly
- [ ] Frontend loads without errors
- [ ] No console errors in browser
- [ ] Existing functionality works as expected

### User Impact Assessment

- [ ] Monitor error rates
- [ ] Monitor authentication success rates
- [ ] Monitor user support tickets
- [ ] Check application performance metrics
- [ ] Verify BetterStack monitoring (if configured)

---

## Rollback Decision Criteria

### Automatic Rollback Triggers

**Rollback immediately if:**
- Authentication success rate drops below 95%
- Error rate increases by >50%
- Application uptime drops below 99%
- Critical user complaints increase
- Database migration fails

### Manual Rollback Consideration

**Consider rollback if:**
- Login loop issue persists
- New bugs introduced
- Performance degradation
- User experience significantly degraded
- Monitoring alerts trigger frequently

---

## Communication Plan

### Rollback Communication

**Internal Team:**
- Notify development team immediately
- Update deployment status in communication channel
- Document rollback reason and steps taken

**Stakeholders:**
- Inform product manager of rollback
- Provide estimated fix timeline
- Communicate user impact assessment

**Users (if needed):**
- Only communicate if user-facing issues occur
- Provide calm, reassuring message
- Explain that improvements are being refined
- No technical details or blame language

---

## Post-Rollback Actions

### Root Cause Analysis

After rollback:
1. Document the exact failure reason
2. Analyze what went wrong
3. Identify necessary fixes
4. Update deployment procedures
5. Plan re-deployment with fixes

### Process Improvement

- Update deployment checklist
- Add additional pre-deployment tests
- Improve monitoring and alerting
- Update rollback procedures based on lessons learned

---

## Rollback Testing

### Pre-Deployment Rollback Test

Before deploying to production, test rollback in staging:

1. Deploy EPIC-002 to staging
2. Simulate failure scenario
3. Execute rollback procedure
4. Verify successful rollback
5. Document any issues found

### Rollback Procedure Validation

Validate rollback procedures regularly:
- Test database rollback
- Test code rollback
- Test configuration rollback
- Verify rollback time estimates

---

## Emergency Contacts

**Primary Rollback Owner:** [TBD]  
**Secondary Rollback Owner:** [TBD]  
**Database Administrator:** [TBD]  
**Infrastructure Team:** [TBD]  

---

## Rollback Log

| Date | Scenario | Reason | Duration | Success |
|------|----------|---------|----------|---------|
| [Pre-deployment] | N/A | N/A | N/A | N/A |

---

## Appendix: Quick Reference Commands

### Git Rollback
```bash
# Revert specific commit
git revert 6559222

# Reset to previous commit (destructive)
git reset --hard HEAD~1

# Check current commit
git log --oneline -1
```

### Database Rollback
```bash
# Check current migration
alembic current

# Rollback one migration
alembic downgrade epic002_account_preferences

# Rollback to specific migration
alembic downgrade <migration_id>
```

### railway.app Rollback
```bash
# Stop application
railway apps stop noni-api

# Redeploy previous version
railway deploy --remote <previous_commit_hash>

# Start application
railway apps start noni-api
```

---

**Rollback Plan Created:** 2026-08-09  
**Rollback Plan Version:** 1.0  
**Next Review Date:** After first deployment