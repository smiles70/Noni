# EPIC-002: Login Loop Fix and Account Setup Flow

**Epic ID:** EPIC-002  
**Epic Name:** Login Loop Fix and Account Setup Flow  
**Status:** PENDING APPROVAL  
**Priority:** CRITICAL  
**Created:** 2026-08-09  
**Methodology:** Process v9 - Full-Stack Agent Harness  
**Sprint:** TDB  

---

## Executive Summary

**CRITICAL ISSUE:** Users experience a login loop where they successfully authenticate but are immediately redirected back to the login/account setup screen. This is a critical blocking issue preventing user access to the application.

**ROOT CAUSE ANALYSIS:**
1. **Clerk Virtual Routing Issue**: The current implementation uses Clerk's deprecated `routing="virtual"` mode, which is known to cause redirect loops in SPA applications. Clerk has deprecated this feature and recommends path-based routing for production applications.
2. **Missing Account Setup Flow**: After successful authentication, users are immediately redirected to curriculum without proper account setup/welcome phase, violating modern SaaS onboarding best practices.
3. **State Synchronization Issue**: The AuthProvider and Clerk widget state can become desynchronized, causing infinite redirect loops between `/signin` and `/`.

**BUSINESS IMPACT:**
- **Users Blocked**: Cannot access the application after successful authentication
- **Conversion Loss**: Users who complete sign-in cannot proceed to the product
- **Support Load**: Increased support tickets for login issues
- **Brand Damage**: Poor first experience undermines confidence in the platform

---

## Investigation Summary

### Current Architecture Analysis

**Authentication Flow:**
1. User navigates to `/signin`
2. SignInPage renders Clerk widget with `routing="virtual"`
3. User completes authentication in Clerk widget
4. AuthProvider detects `isSignedIn` change via `useClerkAuth()`
5. AuthProvider calls `/auth/session` to verify token
6. If `materialized=false`, calls `/auth/session/init` to create account
7. App.tsx redirects to `/curriculum` when state becomes "READY"
8. **BUG**: Clerk widget detects user is already signed in and auto-redirects, creating loop

**Technical Issues Identified:**

1. **Virtual Routing Deprecated**: Clerk deprecated `routing="virtual"` in PR #5072 (Feb 2025) and removed it from public APIs in PR #4977. This mode is known to cause redirect loops in SPAs.

2. **No Account Setup Phase**: The current flow lacks:
   - Welcome screen after successful authentication
   - Profile completion (display name, preferences)
   - Progressive onboarding steps
   - First meaningful action guidance

3. **State Race Condition**: Clerk's auto-redirect behavior (when user is already signed in) races with React Router's redirect logic, causing infinite loops.

### Comparison with Successful SaaS Models

**Best Practices from 2026 SaaS Leaders:**

1. **Authentication Best Practices** (SSOJet, WorkOS):
   - Use path-based routing (not virtual routing)
   - Implement proper session management
   - Handle authentication state transitions gracefully
   - Avoid redirect loops by managing state synchronization

2. **Onboarding Best Practices** (UserOrbit, Skene, Gatilab):
   - **Stage 1: Welcome** (0-5 minutes) - Account setup, profile completion
   - **Stage 2: First Value** (5-30 minutes) - Core feature introduction
   - **Stage 3: Activation** (Days 1-7) - Criteria that correlate with retention
   - **Progressive Profiling**: Collect information over time, not all at once
   - **Forced First Action**: Guide users to complete one meaningful action

3. **Session Management Best Practices**:
   - Proper session timeout handling
   - Secure cookie management (SameSite, Secure attributes)
   - Graceful error handling for transient failures
   - Clear sign-out flow that clears all state

**Current Noni Gaps:**
- ❌ No welcome/account setup phase
- ❌ No profile completion step
- ❌ No progressive onboarding
- ❌ No first meaningful action guidance
- ❌ Uses deprecated virtual routing
- ❌ Prone to redirect loops
- ❌ No session state validation

---

## Epic Objectives

### Primary Objectives

1. **Fix Login Loop**: Eliminate the redirect loop that prevents users from accessing the application after successful authentication
2. **Implement Account Setup Flow**: Add a proper account setup/welcome phase following SaaS best practices
3. **Improve Onboarding Experience**: Implement progressive onboarding to guide users to first value
4. **Enhance Session Management**: Fix session state synchronization issues

### Secondary Objectives

1. **Compliance with Geragogy Contract**: Ensure all UI changes comply with the CONTRACT.md for older adult learners
2. **Monitoring and Telemetry**: Add telemetry tracking for the new onboarding flow
3. **Fallback Strategy**: Implement robust error handling and fallback mechanisms

---

## Scope

### In Scope

**Phase 1: Login Loop Fix (CRITICAL)**
- Replace Clerk `routing="virtual"` with path-based routing
- Fix AuthProvider and Clerk state synchronization
- Implement proper redirect handling
- Add session state validation
- Test authentication flow end-to-end

**Phase 2: Account Setup Flow**
- Create welcome screen after successful authentication
- Implement profile completion step (display name, preferences)
- Add progressive onboarding components
- Implement forced first action guidance
- Create account setup progress tracking

**Phase 3: Onboarding Enhancement**
- Implement progressive profiling
- Add first meaningful action guidance
- Create onboarding completion metrics
- Implement onboarding retry logic
- Add onboarding skip options (with geragogy compliance)

**Phase 4: Monitoring and Fallback**
- Add telemetry tracking for onboarding flow
- Implement error handling and fallback mechanisms
- Create onboarding failure recovery
- Add session validation checks
- Implement session timeout handling

### Out of Scope

- Changes to the authentication provider (Clerk → other)
- Changes to the backend authentication logic
- Changes to the curriculum content
- Changes to the billing/payment flow
- Changes to the existing AuthProvider architecture (unless necessary for fix)

---

## Architecture Changes

### Phase 1: Login Loop Fix

**Current Architecture Issues:**
```
User → /signin → Clerk (virtual routing) → Auth loop
```

**Proposed Architecture:**
```
User → /signin → Clerk (path routing) → /welcome → /curriculum
```

**Technical Changes:**

1. **Clerk Configuration Changes:**
   - Remove `routing="virtual"` from SignIn component
   - Implement path-based routing with Clerk
   - Configure proper redirect URLs in Clerk dashboard
   - Add `signInUrl` and `afterSignInUrl` to ClerkProvider

2. **React Router Changes:**
   - Add `/welcome` route for account setup
   - Add `/setup` route for profile completion
   - Implement proper redirect guards
   - Add route transition validation

3. **AuthProvider Changes:**
   - Fix state synchronization with Clerk
   - Add session validation logic
   - Implement proper error handling
   - Add session timeout detection

### Phase 2: Account Setup Flow

**New Routes:**
- `/welcome` - Welcome screen after authentication
- `/setup` - Profile completion step
- `/getting-started` - Progressive onboarding

**New Components:**
- `WelcomePage` - Welcome screen with account setup introduction
- `AccountSetupPage` - Profile completion form
- `GettingStartedPage` - Progressive onboarding flow
- `OnboardingProgress` - Progress tracking component

**New Backend Endpoints:**
- `PUT /api/v1/account/profile` - Update user profile
- `GET /api/v1/account/onboarding-status` - Get onboarding progress
- `POST /api/v1/account/onboarding-complete` - Mark onboarding complete

### Phase 3: Onboarding Enhancement

**Progressive Profiling:**
- Collect display name in welcome phase
- Collect preferences gradually during curriculum use
- Avoid overwhelming users with too many questions
- Implement skip options with geragogy compliance

**First Meaningful Action:**
- Guide users to start Module 1
- Provide clear next steps
- Celebrate first completion
- Track time-to-first-value metrics

---

## Implementation Plan

### Phase 1: Login Loop Fix (CRITICAL - Sprint 1)

**Sprint Goal:** Fix the login loop blocking user access

**Tasks:**

1. **Replace Virtual Routing with Path Routing**
   - Update ClerkProvider configuration in `main.tsx`
   - Remove `routing="virtual"` from SignIn component
   - Configure `signInUrl` and `afterSignInUrl` in ClerkProvider
   - Update Clerk dashboard redirect URLs
   - Test authentication flow

2. **Fix AuthProvider State Synchronization**
   - Add session validation logic in AuthProvider
   - Implement proper error handling for Clerk state changes
   - Add session timeout detection
   - Fix race conditions between Clerk and React Router
   - Add debug logging for state transitions

3. **Implement Proper Redirect Handling**
   - Add `/welcome` route to React Router
   - Update App.tsx redirect logic
   - Implement proper redirect guards
   - Add route transition validation
   - Test redirect flow end-to-end

4. **Add Session State Validation**
   - Implement session validation checks
   - Add session timeout handling
   - Implement proper sign-out flow
   - Clear all state on sign-out
   - Test session lifecycle

5. **Testing and Validation**
   - Unit tests for AuthProvider
   - Integration tests for authentication flow
   - E2E tests for login flow
   - Test with different browsers
   - Test with private/incognito mode

**Acceptance Criteria:**
- ✅ Users can successfully authenticate without redirect loops
- ✅ AuthProvider state remains synchronized with Clerk
- ✅ Users are redirected to `/welcome` after successful authentication
- ✅ Session state is properly validated on each request
- ✅ Sign-out clears all state correctly
- ✅ All tests pass

### Phase 2: Account Setup Flow (Sprint 2)

**Sprint Goal:** Implement account setup flow following SaaS best practices

**Tasks:**

1. **Create Welcome Page**
   - Create `WelcomePage` component
   - Implement welcome screen with account setup introduction
   - Add geragogy-compliant design (CONTRACT.md)
   - Implement progress tracking
   - Add telemetry tracking

2. **Create Account Setup Page**
   - Create `AccountSetupPage` component
   - Implement profile completion form (display name, preferences)
   - Add form validation
   - Implement progressive profiling
   - Add geragogy-compliant design

3. **Backend Profile Update Endpoint**
   - Create `PUT /api/v1/account/profile` endpoint
   - Implement profile update logic
   - Add validation
   - Add error handling
   - Add telemetry tracking

4. **Backend Onboarding Status Endpoint**
   - Create `GET /api/v1/account/onboarding-status` endpoint
   - Implement onboarding progress tracking
   - Add status logic
   - Add caching
   - Add telemetry tracking

5. **Integrate with Auth Flow**
   - Update App.tsx to redirect to `/welcome` after authentication
   - Implement onboarding completion detection
   - Add redirect logic for completed onboarding
   - Update AuthProvider to handle onboarding state
   - Test end-to-end flow

6. **Testing and Validation**
   - Unit tests for new components
   - Integration tests for profile update flow
   - E2E tests for account setup flow
   - Test geragogy compliance
   - Test with assistive technologies

**Acceptance Criteria:**
- ✅ Users see welcome screen after successful authentication
- ✅ Users can complete profile setup
- ✅ Profile data is saved to backend
- ✅ Onboarding progress is tracked
- ✅ Users are redirected to curriculum after setup
- ✅ All UI complies with CONTRACT.md
- ✅ All tests pass

### Phase 3: Onboarding Enhancement (Sprint 3)

**Sprint Goal:** Implement progressive onboarding to guide users to first value

**Tasks:**

1. **Create Getting Started Page**
   - Create `GettingStartedPage` component
   - Implement progressive onboarding flow
   - Add step-by-step guidance
   - Implement forced first action guidance
   - Add geragogy-compliant design

2. **Implement Progressive Profiling**
   - Add preference collection during curriculum use
   - Implement skip options with geragogy compliance
   - Add progressive question display
   - Implement preference persistence
   - Add telemetry tracking

3. **First Meaningful Action Guidance**
   - Add guidance to start Module 1
   - Implement clear next steps
   - Add celebration for first completion
   - Track time-to-first-value metrics
   - Add progress tracking

4. **Onboarding Completion Logic**
   - Implement onboarding completion detection
   - Add completion metrics
   - Implement completion celebration
   - Add completion telemetry
   - Update user state on completion

5. **Testing and Validation**
   - Unit tests for onboarding components
   - Integration tests for onboarding flow
   - E2E tests for onboarding completion
   - Test geragogy compliance
   - Test time-to-first-value metrics

**Acceptance Criteria:**
- ✅ Users receive progressive onboarding guidance
- ✅ Users complete first meaningful action
- ✅ Onboarding completion is tracked
- ✅ Time-to-first-value is measured
- ✅ All UI complies with CONTRACT.md
- ✅ All tests pass

### Phase 4: Monitoring and Fallback (Sprint 4)

**Sprint Goal:** Add monitoring and fallback mechanisms for robust onboarding

**Tasks:**

1. **Add Telemetry Tracking**
   - Track onboarding step completion
   - Track onboarding abandonment
   - Track time-to-completion
   - Track error rates
   - Add BetterStack integration

2. **Implement Error Handling**
   - Add error handling for onboarding steps
   - Implement retry logic
   - Add error recovery mechanisms
   - Implement graceful degradation
   - Add error telemetry

3. **Session Validation**
   - Add session validation checks
   - Implement session timeout handling
   - Add session refresh logic
   - Implement session recovery
   - Add session telemetry

4. **Fallback Mechanisms**
   - Implement fallback for onboarding failures
   - Add skip options with geragogy compliance
   - Implement recovery flows
   - Add fallback telemetry
   - Test fallback scenarios

5. **Testing and Validation**
   - Unit tests for error handling
   - Integration tests for fallback flows
   - E2E tests for error scenarios
   - Test telemetry integration
   - Test with network failures

**Acceptance Criteria:**
- ✅ Onboarding telemetry is tracked
- ✅ Errors are handled gracefully
- ✅ Session validation works correctly
- ✅ Fallback mechanisms function properly
- ✅ BetterStack integration works
- ✅ All tests pass

---

## Success Metrics

### Phase 1: Login Loop Fix

**Technical Metrics:**
- ✅ Login loop issue resolved (0 occurrences)
- ✅ Authentication success rate > 99%
- ✅ Session state synchronization rate 100%
- ✅ Redirect loop rate 0%
- ✅ Session validation success rate > 99%

**User Metrics:**
- ✅ Users can authenticate successfully
- ✅ Users can access the application after authentication
- ✅ Time-to-first-access < 5 seconds
- ✅ Authentication error rate < 1%

### Phase 2: Account Setup Flow

**Technical Metrics:**
- ✅ Account setup completion rate > 90%
- ✅ Profile update success rate > 99%
- ✅ Onboarding progress tracking accuracy 100%
- ✅ API response time < 500ms
- ✅ Error rate < 1%

**User Metrics:**
- ✅ Users complete account setup
- ✅ Time-to-setup-completion < 3 minutes
- ✅ Setup abandonment rate < 10%
- ✅ User satisfaction score > 4.5/5

### Phase 3: Onboarding Enhancement

**Technical Metrics:**
- ✅ Onboarding completion rate > 85%
- ✅ Progressive profiling completion rate > 80%
- ✅ First meaningful action completion rate > 90%
- ✅ Time-to-first-value < 10 minutes
- ✅ Error rate < 2%

**User Metrics:**
- ✅ Users complete onboarding
- ✅ Users reach first meaningful action
- ✅ Onboarding abandonment rate < 15%
- ✅ User engagement after onboarding > 70%

### Phase 4: Monitoring and Fallback

**Technical Metrics:**
- ✅ Telemetry tracking coverage 100%
- ✅ Error handling success rate > 95%
- ✅ Session validation success rate > 99%
- ✅ Fallback mechanism success rate > 90%
- ✅ BetterStack integration working

**User Metrics:**
- ✅ Users experience minimal errors
- ✅ Error recovery rate > 80%
- ✅ Session interruption rate < 5%
- ✅ User satisfaction with error handling > 4.0/5

---

## Risk Assessment

### Technical Risks

**Risk 1: Clerk Path Routing Migration Complexity**
- **Severity:** HIGH
- **Mitigation:** Thorough testing in staging environment
- **Contingency:** Roll back to virtual routing with loop fix
- **Owner:** Backend Team

**Risk 2: AuthProvider State Synchronization**
- **Severity:** HIGH
- **Mitigation:** Comprehensive state validation logic
- **Contingency:** Implement fallback session validation
- **Owner:** Frontend Team

**Risk 3: Onboarding Flow Complexity**
- **Severity:** MEDIUM
- **Mitigation:** Incremental implementation with testing
- **Contingency:** Simplify onboarding if issues arise
- **Owner:** Product Team

### Operational Risks

**Risk 4: User Confusion During Migration**
- **Severity:** MEDIUM
- **Mitigation:** Clear communication and gradual rollout
- **Contingency:** Revert changes if user impact is high
- **Owner:** Product Team

**Risk 5: Performance Impact**
- **Severity:** LOW
- **Mitigation:** Performance testing and optimization
- **Contingency:** Optimize critical paths
- **Owner:** Engineering Team

**Risk 6: Geragogy Compliance Issues**
- **Severity:** MEDIUM
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

## Timeline

**Phase 1: Login Loop Fix**
- **Start:** Week 1
- **End:** Week 2
- **Milestone:** Login loop resolved

**Phase 2: Account Setup Flow**
- **Start:** Week 3
- **End:** Week 4
- **Milestone:** Account setup flow live

**Phase 3: Onboarding Enhancement**
- **Start:** Week 5
- **End:** Week 6
- **Milestone:** Progressive onboarding live

**Phase 4: Monitoring and Fallback**
- **Start:** Week 7
- **End:** Week 8
- **Milestone:** Monitoring and fallback complete

**Total Timeline:** 8 weeks

---

## Deliverables

### Phase 1 Deliverables

1. **Updated Clerk Configuration**
   - Path-based routing implementation
   - Proper redirect URLs
   - Configuration documentation

2. **Fixed AuthProvider**
   - State synchronization fixes
   - Session validation logic
   - Error handling improvements

3. **Updated React Router**
   - New `/welcome` route
   - Improved redirect logic
   - Route transition validation

4. **Test Suite**
   - Unit tests
   - Integration tests
   - E2E tests

5. **Documentation**
   - Authentication flow documentation
   - Troubleshooting guide
   - API documentation updates

### Phase 2 Deliverables

1. **Welcome Page Component**
   - Geragogy-compliant design
   - Progress tracking
   - Telemetry integration

2. **Account Setup Page Component**
   - Profile completion form
   - Progressive profiling
   - Geragogy-compliant design

3. **Backend Endpoints**
   - Profile update endpoint
   - Onboarding status endpoint
   - API documentation

4. **Database Schema**
   - Onboarding progress tracking
   - User preferences
   - Migration scripts

5. **Test Suite**
   - Unit tests
   - Integration tests
   - E2E tests

6. **Documentation**
   - Account setup guide
   - API documentation
   - User guide

### Phase 3 Deliverables

1. **Getting Started Page Component**
   - Progressive onboarding flow
   - Step-by-step guidance
   - Geragogy-compliant design

2. **Progressive Profiling**
   - Preference collection
   - Skip options
   - Geragogy compliance

3. **First Meaningful Action Guidance**
   - Clear next steps
   - Celebration logic
   - Progress tracking

4. **Test Suite**
   - Unit tests
   - Integration tests
   - E2E tests

5. **Documentation**
   - Onboarding guide
   - Progressive profiling guide
   - User guide

### Phase 4 Deliverables

1. **Telemetry Integration**
   - Onboarding step tracking
   - Error tracking
   - BetterStack integration

2. **Error Handling**
   - Error recovery mechanisms
   - Fallback logic
   - Error telemetry

3. **Session Validation**
   - Session validation checks
   - Session timeout handling
   - Session recovery

4. **Test Suite**
   - Unit tests
   - Integration tests
   - E2E tests

5. **Documentation**
   - Monitoring guide
   - Troubleshooting guide
   - Operations guide

---

## Success Criteria

### Epic Success Criteria

**Must Have (Mandatory):**
- ✅ Login loop issue completely resolved
- ✅ Users can successfully authenticate and access the application
- ✅ Account setup flow implemented and functional
- ✅ Onboarding flow implemented and functional
- ✅ All UI complies with CONTRACT.md (geragogy compliance)
- ✅ All tests pass
- ✅ Monitoring and telemetry integrated

**Should Have (Expected):**
- ✅ Account setup completion rate > 90%
- ✅ Onboarding completion rate > 85%
- ✅ Time-to-first-value < 10 minutes
- ✅ User satisfaction score > 4.5/5
- ✅ Error rate < 2%

**Could Have (Nice to Have):**
- ✅ Progressive profiling completion rate > 80%
- ✅ First meaningful action completion rate > 90%
- ✅ Session validation success rate > 99%
- ✅ Fallback mechanism success rate > 90%

### Phase Success Criteria

**Phase 1 Success Criteria:**
- ✅ Login loop issue resolved
- ✅ Authentication success rate > 99%
- ✅ Session state synchronization rate 100%
- ✅ All tests pass

**Phase 2 Success Criteria:**
- ✅ Account setup flow functional
- ✅ Account setup completion rate > 90%
- ✅ Profile update success rate > 99%
- ✅ All tests pass

**Phase 3 Success Criteria:**
- ✅ Onboarding flow functional
- ✅ Onboarding completion rate > 85%
- ✅ Time-to-first-value < 10 minutes
- ✅ All tests pass

**Phase 4 Success Criteria:**
- ✅ Monitoring integrated
- ✅ Telemetry tracking functional
- ✅ Error handling functional
- ✅ All tests pass

---

## Rollout Plan

### Phase 1 Rollout (Critical Fix)

**Staging Deployment:**
1. Deploy to staging environment
2. Test authentication flow end-to-end
3. Test with different browsers
4. Test with private/incognito mode
5. Validate session state synchronization
6. Fix any issues found

**Production Deployment:**
1. Deploy during low-traffic period
2. Monitor authentication success rate
3. Monitor for login loop occurrences
4. Have rollback plan ready
5. Communicate deployment to team

**Post-Deployment:**
1. Monitor authentication metrics
2. Monitor user feedback
3. Fix any issues that arise
4. Update documentation

### Phase 2 Rollout

**Staging Deployment:**
1. Deploy to staging environment
2. Test account setup flow end-to-end
3. Test profile update functionality
4. Test onboarding progress tracking
5. Validate geragogy compliance
6. Fix any issues found

**Production Deployment:**
1. Deploy during low-traffic period
2. Monitor account setup completion rate
3. Monitor profile update success rate
4. Monitor user feedback
5. Have rollback plan ready

**Post-Deployment:**
1. Monitor onboarding metrics
2. Monitor user feedback
3. Fix any issues that arise
4. Update documentation

### Phase 3 Rollout

**Staging Deployment:**
1. Deploy to staging environment
2. Test onboarding flow end-to-end
3. Test progressive profiling
4. Test first meaningful action guidance
5. Validate geragogy compliance
6. Fix any issues found

**Production Deployment:**
1. Deploy during low-traffic period
2. Monitor onboarding completion rate
3. Monitor time-to-first-value
4. Monitor user feedback
5. Have rollback plan ready

**Post-Deployment:**
1. Monitor onboarding metrics
2. Monitor user engagement
3. Fix any issues that arise
4. Update documentation

### Phase 4 Rollout

**Staging Deployment:**
1. Deploy to staging environment
2. Test telemetry integration
3. Test error handling
4. Test session validation
5. Test fallback mechanisms
6. Fix any issues found

**Production Deployment:**
1. Deploy during low-traffic period
2. Monitor telemetry data
3. Monitor error rates
4. Monitor session validation
5. Have rollback plan ready

**Post-Deployment:**
1. Monitor all metrics
2. Monitor user feedback
3. Fix any issues that arise
4. Update documentation

---

## Conclusion

This epic addresses the critical login loop issue and implements a comprehensive account setup and onboarding flow following modern SaaS best practices. The implementation is broken down into 4 phases over 8 weeks, with clear success criteria and rollback plans.

**Key Benefits:**
- **Fixes Critical Issue:** Resolves login loop blocking user access
- **Improves User Experience:** Implements proper account setup and onboarding
- **Follows Best Practices:** Aligns with 2026 SaaS onboarding standards
- **Geragogy Compliant:** Ensures accessibility for older adult learners
- **Monitoring:** Comprehensive telemetry and error handling
- **Scalable:** Foundation for future onboarding enhancements

**Next Steps:**
1. Review and approve this epic
2. Assign team members to phases
3. Set up external dependencies (Clerk dashboard, BetterStack)
4. Begin Phase 1 implementation

---

**Epic Created By:** Process v9 - Full-Stack Agent Harness  
**Epic Methodology:** Process v9 - Investigation, Analysis, Planning  
**Epic Date:** 2026-08-09  
**Epic Status:** PENDING APPROVAL