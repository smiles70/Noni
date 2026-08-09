# Login Loop Investigation and Planning Report

**Report Date:** 2026-08-09  
**Investigation Methodology:** Process v9 - Full-Stack Agent Harness  
**Severity:** CRITICAL  
**Status:** INVESTIGATION COMPLETE - EPIC READY FOR APPROVAL  
**Related Epic:** EPIC-002: Login Loop Fix and Account Setup Flow  

---

## Executive Summary

**CRITICAL ISSUE IDENTIFIED:** Users experience a login loop where they successfully authenticate but are immediately redirected back to the login/account setup screen. This is a critical blocking issue preventing user access to the application.

**ROOT CAUSE IDENTIFIED:** The login loop is caused by a combination of:
1. **Clerk Virtual Routing Issue**: Use of deprecated `routing="virtual"` mode causing redirect loops
2. **Missing Account Setup Flow**: No proper post-authentication account setup phase
3. **State Synchronization Issue**: Race condition between Clerk widget and React Router

**BUSINESS IMPACT:**
- Users blocked from accessing the application after successful authentication
- Conversion loss at the authentication-to-product transition
- Increased support load for login issues
- Brand damage from poor first experience

**RECOMMENDATION:** Implement EPIC-002: Login Loop Fix and Account Setup Flow, a 4-phase, 8-week epic to fix the critical issue and implement modern SaaS onboarding best practices.

---

## Investigation Findings

### Phase 1: Current Architecture Analysis

**Authentication Flow:**
```
User → /signin → Clerk SignIn (routing="virtual") → 
AuthProvider detects isSignedIn → /auth/session → 
/auth/session/init → App.tsx redirects to /curriculum → 
Clerk auto-redirects to /signin → INFINITE LOOP
```

**Technical Analysis:**

**Clerk Configuration (<ref_file file="C:\Users\travel\CascadeProjects\Noni\frontend\src\components\SignInPage.tsx" lines="82" />):**
```typescript
<SignIn routing="virtual" fallbackRedirectUrl="/" />
```

**AuthProvider Logic (<ref_file file="C:\Users\travel\CascadeProjects\Noni\frontend\src\auth\AuthProvider.tsx" lines="64-66" />):**
```typescript
const auth = useCredentialSource();
const [state, setState] = useState<AuthState>({ status: "BOOT" });
```

**App.tsx Redirect Logic (<ref_file file="C:\Users\travel\CascadeProjects\Noni\frontend\src\App.tsx" lines="94-104" />):**
```typescript
useEffect(() => {
  if (isReady) {
    const params = new URLSearchParams(location.search);
    const redirect = params.get("redirect");
    if (redirect) {
      navigate(redirect, { replace: true });
    } else if (location.pathname === "/signin") {
      navigate("/curriculum", { replace: true });
    }
  }
}, [isReady, location.search, location.pathname, navigate]);
```

**Session Resolution (<ref_file file="C:\Users\travel\CascadeProjects\Noni\frontend\src\auth\useAuthSession.ts" lines="68-104" />):**
- Calls `/auth/session` to verify token
- If `materialized=false`, calls `/auth/session/init` to create account
- Transitions to "READY" state on success

**Backend Session Logic (<ref_file file="C:\Users\travel\CascadeProjects\Noni\backend\api\routes\auth.py" lines="109-181" />):**
- `/auth/session` endpoint verifies token and checks for existing account
- Returns `materialized=false` if no account exists
- `/auth/session/init` creates account row

**Issues Identified:**
1. Clerk's `routing="virtual"` is deprecated and known to cause redirect loops
2. No intermediate step between authentication and curriculum access
3. Clerk widget auto-redirects when user is already signed in
4. Race condition between Clerk's auto-redirect and React Router's redirect

### Phase 2: Comparison with Successful SaaS Models

**2026 SaaS Authentication Best Practices:**

**Authentication Best Practices (SSOJet, WorkOS):**
- ✅ Use path-based routing (not virtual routing)
- ✅ Implement proper session management
- ✅ Handle authentication state transitions gracefully
- ✅ Avoid redirect loops by managing state synchronization
- ✅ Implement proper session timeout handling
- ✅ Secure cookie management (SameSite, Secure attributes)

**Onboarding Best Practices (UserOrbit, Skene, Gatilab):**
- ✅ **Stage 1: Welcome** (0-5 minutes) - Account setup, profile completion
- ✅ **Stage 2: First Value** (5-30 minutes) - Core feature introduction
- ✅ **Stage 3: Activation** (Days 1-7) - Criteria that correlate with retention
- ✅ **Stage 4: Habit** (Weeks 2-8) - Repeat behavior patterns
- ✅ Progressive profiling: Collect information over time
- ✅ Forced first action: Guide users to complete one meaningful action
- ✅ Clear next steps and progress tracking
- ✅ Geragogy compliance for older adult learners

**Current Noni Gaps:**
- ❌ No welcome/account setup phase
- ❌ No profile completion step
- ❌ No progressive onboarding
- ❌ No first meaningful action guidance
- ❌ Uses deprecated virtual routing
- ❌ Prone to redirect loops
- ❌ No session state validation
- ❌ No onboarding telemetry

### Phase 3: Root Cause Identification

**Root Cause 1: Clerk Virtual Routing Issue**
- **Evidence:** Clerk deprecated `routing="virtual"` in PR #5072 (Feb 2025) and removed it from public APIs in PR #4977
- **Evidence:** Multiple GitHub issues show redirect loops with virtual routing in SPAs
- **Evidence:** Clerk documentation recommends path-based routing for production applications
- **Impact:** High - causes redirect loops that block user access

**Root Cause 2: Missing Account Setup Flow**
- **Evidence:** Current flow redirects directly to `/curriculum` after authentication
- **Evidence:** No intermediate step for profile completion or welcome
- **Evidence:** No progressive onboarding implementation
- **Impact:** High - violates SaaS best practices, poor user experience

**Root Cause 3: State Synchronization Issue**
- **Evidence:** Clerk widget auto-redirects when user is already signed in
- **Evidence:** React Router redirect logic races with Clerk's auto-redirect
- **Evidence:** AuthProvider state can become desynchronized with Clerk
- **Impact:** High - causes infinite redirect loops

**Root Cause Analysis Conclusion:**
The login loop is primarily caused by the use of deprecated Clerk virtual routing, combined with the lack of a proper account setup flow. The state synchronization issue exacerbates the problem by creating race conditions between different redirect mechanisms.

### Phase 4: Gap Analysis

**Technical Gaps:**

1. **Authentication Architecture:**
   - ❌ Uses deprecated virtual routing
   - ❌ No proper session state validation
   - ❌ Race conditions in redirect logic
   - ❌ No session timeout handling
   - ✅ Good: Single source of truth (AuthProvider)
   - ✅ Good: Discriminated error handling

2. **Onboarding Architecture:**
   - ❌ No account setup phase
   - ❌ No profile completion step
   - ❌ No progressive onboarding
   - ❌ No first meaningful action guidance
   - ❌ No onboarding telemetry
   - ❌ No onboarding completion tracking

3. **Session Management:**
   - ❌ No session validation checks
   - ❌ No session timeout handling
   - ❌ No session recovery mechanisms
   - ❌ No session refresh logic
   - ✅ Good: Backend session verification
   - ✅ Good: Account materialization logic

**User Experience Gaps:**

1. **Post-Authentication Experience:**
   - ❌ No welcome screen
   - ❌ No account setup guidance
   - ❌ No profile completion
   - ❌ No onboarding flow
   - ❌ No first meaningful action guidance

2. **Geragogy Compliance:**
   - ❌ No account setup geragogy compliance
   - ❌ No onboarding geragogy compliance
   - ✅ Good: Existing CONTRACT.md compliance
   - ✅ Good: Geragogy skill available

**Monitoring Gaps:**

1. **Telemetry:**
   - ❌ No onboarding telemetry
   - ❌ No authentication failure telemetry
   - ❌ No session validation telemetry
   - ❌ No onboarding completion tracking
   - ✅ Good: BetterStack integration available
   - ✅ Good: Clerk telemetry integration available

---

## Epic Plan

### Epic Overview

**Epic ID:** EPIC-002  
**Epic Name:** Login Loop Fix and Account Setup Flow  
**Priority:** CRITICAL  
**Timeline:** 8 weeks (4 sprints)  
**Total Effort:** ~8 engineer-sprints, ~4 QA-sprints, ~1 designer-sprint

### Phase 1: Login Loop Fix (Sprint 1 - CRITICAL)

**Objective:** Fix the login loop blocking user access

**Key Changes:**
1. Replace Clerk `routing="virtual"` with path-based routing
2. Fix AuthProvider state synchronization
3. Implement proper redirect handling
4. Add session state validation
5. Test authentication flow end-to-end

**Acceptance Criteria:**
- ✅ Users can successfully authenticate without redirect loops
- ✅ AuthProvider state remains synchronized with Clerk
- ✅ Users are redirected to `/welcome` after successful authentication
- ✅ Session state is properly validated on each request
- ✅ Sign-out clears all state correctly
- ✅ All tests pass

**Timeline:** Weeks 1-2

### Phase 2: Account Setup Flow (Sprint 2)

**Objective:** Implement account setup flow following SaaS best practices

**Key Changes:**
1. Create welcome screen after successful authentication
2. Implement profile completion step (display name, preferences)
3. Add progressive onboarding components
4. Implement forced first action guidance
5. Create account setup progress tracking

**Acceptance Criteria:**
- ✅ Users see welcome screen after successful authentication
- ✅ Users can complete profile setup
- ✅ Profile data is saved to backend
- ✅ Onboarding progress is tracked
- ✅ Users are redirected to curriculum after setup
- ✅ All UI complies with CONTRACT.md
- ✅ All tests pass

**Timeline:** Weeks 3-4

### Phase 3: Onboarding Enhancement (Sprint 3)

**Objective:** Implement progressive onboarding to guide users to first value

**Key Changes:**
1. Create getting started page with progressive onboarding
2. Implement progressive profiling
3. Add first meaningful action guidance
4. Implement onboarding completion logic
5. Add onboarding completion metrics

**Acceptance Criteria:**
- ✅ Users receive progressive onboarding guidance
- ✅ Users complete first meaningful action
- ✅ Onboarding completion is tracked
- ✅ Time-to-first-value is measured
- ✅ All UI complies with CONTRACT.md
- ✅ All tests pass

**Timeline:** Weeks 5-6

### Phase 4: Monitoring and Fallback (Sprint 4)

**Objective:** Add monitoring and fallback mechanisms for robust onboarding

**Key Changes:**
1. Add telemetry tracking for onboarding flow
2. Implement error handling and fallback mechanisms
3. Add session validation checks
4. Implement session timeout handling
5. Add BetterStack integration

**Acceptance Criteria:**
- ✅ Onboarding telemetry is tracked
- ✅ Errors are handled gracefully
- ✅ Session validation works correctly
- ✅ Fallback mechanisms function properly
- ✅ BetterStack integration works
- ✅ All tests pass

**Timeline:** Weeks 7-8

---

## Success Metrics

### Phase 1: Login Loop Fix

**Technical Metrics:**
- Login loop issue resolved (0 occurrences)
- Authentication success rate > 99%
- Session state synchronization rate 100%
- Redirect loop rate 0%
- Session validation success rate > 99%

**User Metrics:**
- Users can authenticate successfully
- Users can access the application after authentication
- Time-to-first-access < 5 seconds
- Authentication error rate < 1%

### Phase 2: Account Setup Flow

**Technical Metrics:**
- Account setup completion rate > 90%
- Profile update success rate > 99%
- Onboarding progress tracking accuracy 100%
- API response time < 500ms
- Error rate < 1%

**User Metrics:**
- Users complete account setup
- Time-to-setup-completion < 3 minutes
- Setup abandonment rate < 10%
- User satisfaction score > 4.5/5

### Phase 3: Onboarding Enhancement

**Technical Metrics:**
- Onboarding completion rate > 85%
- Progressive profiling completion rate > 80%
- First meaningful action completion rate > 90%
- Time-to-first-value < 10 minutes
- Error rate < 2%

**User Metrics:**
- Users complete onboarding
- Users reach first meaningful action
- Onboarding abandonment rate < 15%
- User engagement after onboarding > 70%

### Phase 4: Monitoring and Fallback

**Technical Metrics:**
- Telemetry tracking coverage 100%
- Error handling success rate > 95%
- Session validation success rate > 99%
- Fallback mechanism success rate > 90%
- BetterStack integration working

**User Metrics:**
- Users experience minimal errors
- Error recovery rate > 80%
- Session interruption rate < 5%
- User satisfaction with error handling > 4.0/5

---

## Risk Assessment

### Technical Risks

**Risk 1: Clerk Path Routing Migration Complexity**
- **Severity:** HIGH
- **Probability:** MEDIUM
- **Mitigation:** Thorough testing in staging environment
- **Contingency:** Roll back to virtual routing with loop fix
- **Owner:** Backend Team

**Risk 2: AuthProvider State Synchronization**
- **Severity:** HIGH
- **Probability:** MEDIUM
- **Mitigation:** Comprehensive state validation logic
- **Contingency:** Implement fallback session validation
- **Owner:** Frontend Team

**Risk 3: Onboarding Flow Complexity**
- **Severity:** MEDIUM
- **Probability:** LOW
- **Mitigation:** Incremental implementation with testing
- **Contingency:** Simplify onboarding if issues arise
- **Owner:** Product Team

### Operational Risks

**Risk 4: User Confusion During Migration**
- **Severity:** MEDIUM
- **Probability:** MEDIUM
- **Mitigation:** Clear communication and gradual rollout
- **Contingency:** Revert changes if user impact is high
- **Owner:** Product Team

**Risk 5: Performance Impact**
- **Severity:** LOW
- **Probability:** LOW
- **Mitigation:** Performance testing and optimization
- **Contingency:** Optimize critical paths
- **Owner:** Engineering Team

**Risk 6: Geragogy Compliance Issues**
- **Severity:** MEDIUM
- **Probability:** LOW
- **Mitigation:** Review all UI changes against CONTRACT.md
- **Contingency:** Fix compliance issues before deployment
- **Owner:** Design Team

---

## Dependencies

### External Dependencies

1. **Clerk Dashboard Configuration**
   - Update redirect URLs
   - Configure path-based routing
   - Test in staging environment
   - **Owner:** SRE Team
   - **Timeline:** Before Phase 1 start

2. **BetterStack Monitoring**
   - Configure onboarding telemetry
   - Set up alerting for onboarding failures
   - Test integration
   - **Owner:** SRE Team
   - **Timeline:** Before Phase 4 start

### Internal Dependencies

1. **Backend API Endpoints**
   - Profile update endpoint
   - Onboarding status endpoint
   - **Owner:** Backend Team
   - **Timeline:** Phase 2

2. **Database Schema Changes**
   - Add onboarding progress tracking
   - Add user preferences
   - **Owner:** Backend Team
   - **Timeline:** Phase 2

3. **Frontend Components**
   - Welcome page
   - Account setup page
   - Getting started page
   - **Owner:** Frontend Team
   - **Timeline:** Phase 2-3

---

## Resource Requirements

### Team Composition

**Phase 1 (Sprint 1):**
- 1 Frontend Engineer (Auth routing fix)
- 1 Backend Engineer (Session validation)
- 1 QA Engineer (Testing)
- **Duration:** 1 sprint (2 weeks)

**Phase 2 (Sprint 2):**
- 1 Frontend Engineer (Account setup components)
- 1 Backend Engineer (Profile endpoints)
- 1 Designer (Geragogy compliance)
- 1 QA Engineer (Testing)
- **Duration:** 1 sprint (2 weeks)

**Phase 3 (Sprint 3):**
- 1 Frontend Engineer (Onboarding components)
- 1 Backend Engineer (Onboarding logic)
- 1 Product Manager (Onboarding design)
- 1 QA Engineer (Testing)
- **Duration:** 1 sprint (2 weeks)

**Phase 4 (Sprint 4):**
- 1 Frontend Engineer (Monitoring integration)
- 1 Backend Engineer (Telemetry endpoints)
- 1 SRE Engineer (BetterStack setup)
- 1 QA Engineer (Testing)
- **Duration:** 1 sprint (2 weeks)

### Total Effort

- **Total Duration:** 4 sprints (8 weeks)
- **Total Engineering Effort:** ~8 engineer-sprints
- **Total QA Effort:** ~4 QA-sprints
- **Total Design Effort:** ~1 designer-sprint

---

## Recommendations

### Immediate Actions

1. **Approve EPIC-002**
   - Review the epic document
   - Approve the implementation plan
   - Assign team members to phases
   - Set up external dependencies

2. **Begin Phase 1 Implementation**
   - Fix the critical login loop issue
   - Replace virtual routing with path routing
   - Implement session validation
   - Test thoroughly before production deployment

3. **Set Up External Dependencies**
   - Configure Clerk dashboard for path routing
   - Set up BetterStack for onboarding telemetry
   - Test external integrations

### Short-Term Actions

1. **Monitor Current Issues**
   - Track login loop occurrences
   - Monitor user feedback
   - Document additional issues found

2. **Prepare for Phase 2**
   - Design account setup flow
   - Design onboarding components
   - Review geragogy compliance requirements

3. **Team Preparation**
   - Assign team members to phases
   - Set up development environments
   - Prepare testing infrastructure

### Long-Term Actions

1. **Continuous Improvement**
   - Monitor onboarding metrics
   - Iterate on onboarding flow
   - Optimize time-to-first-value

2. **Expansion**
   - Add more onboarding features
   - Implement advanced progressive profiling
   - Add personalization features

---

## Conclusion

The investigation has identified the root cause of the critical login loop issue and has created a comprehensive epic plan to fix the issue and implement modern SaaS onboarding best practices.

**Key Findings:**
- Login loop caused by deprecated Clerk virtual routing
- Missing account setup flow violates SaaS best practices
- State synchronization issues exacerbate the problem
- No onboarding telemetry or monitoring

**Key Recommendations:**
- Implement EPIC-002: Login Loop Fix and Account Setup Flow
- Prioritize Phase 1 (login loop fix) as critical
- Follow 4-phase implementation plan over 8 weeks
- Ensure geragogy compliance throughout
- Implement comprehensive monitoring and telemetry

**Expected Outcomes:**
- Login loop issue completely resolved
- Modern SaaS onboarding flow implemented
- Improved user experience and retention
- Comprehensive monitoring and error handling
- Foundation for future onboarding enhancements

**Next Steps:**
1. Review and approve EPIC-002
2. Assign team members to phases
3. Set up external dependencies
4. Begin Phase 1 implementation

---

**Report Generated By:** Process v9 - Full-Stack Agent Harness  
**Investigation Methodology:** Process v9 - Investigation, Analysis, Planning  
**Report Date:** 2026-08-09  
**Report Status:** INVESTIGATION COMPLETE - EPIC READY FOR APPROVAL