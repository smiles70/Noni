# BetterStack Quick Start Guide

**Version:** 1.0.0  
**Owner:** SRE Team  
**Last Updated:** 2026-08-08

---

## Overview

This guide provides a quick start for configuring BetterStack monitoring for the Noni platform. The implementation includes uptime monitors, log sources, alert rules, and dashboards.

---

## Prerequisites

- BetterStack account (https://betterstack.com)
- BetterStack API key
- Fly.io CLI access
- Cloudflare account access
- Noni backend deployed to Fly.io
- Noni frontend deployed to Cloudflare Pages

---

## Step 1: BetterStack Account Setup

### 1.1 Create Account

1. Navigate to https://betterstack.com
2. Click "Start for free"
3. Sign up or log in
4. Navigate to the dashboard

### 1.2 Get API Key

1. Navigate to Settings → API Keys
2. Create new API key
3. Copy the API key
4. Add to environment configuration:

```bash
# .env
BETTERSTACK_API_KEY=your_api_key_here
BETTERSTACK_SOURCE_NAME=noni-api
```

---

## Step 2: Uptime Monitors

### 2.1 Backend Health Monitor

**Manual Setup:**
1. Navigate to Monitors → Uptime
2. Click "New Monitor"
3. Configure:
   - **Name:** Noni API Health
   - **Type:** HTTP
   - **URL:** `https://noni-api.fly.dev/health`
   - **Method:** GET
   - **Expected Status:** 200
   - **Check Interval:** 30 seconds
   - **Regions:** US East, US West, EU West
   - **Alert Threshold:** 2 consecutive failures

### 2.2 Frontend Availability Monitor

**Manual Setup:**
1. Navigate to Monitors → Uptime
2. Click "New Monitor"
3. Configure:
   - **Name:** Noni Frontend
   - **Type:** HTTP
   - **URL:** `https://noni-web.pages.dev`
   - **Method:** GET
   - **Expected Status:** 200
   - **Check Interval:** 60 seconds
   - **Regions:** US East, US West, EU West
   - **Alert Threshold:** 3 consecutive failures

### 2.3 Auth Endpoint Monitor

**Manual Setup:**
1. Navigate to Monitors → Uptime
2. Click "New Monitor"
3. Configure:
   - **Name:** Noni Auth Config
   - **Type:** HTTP
   - **URL:** `https://noni-api.fly.dev/api/v1/auth/config`
   - **Method:** GET
   - **Expected Status:** 200
   - **Check Interval:** 60 seconds
   - **Regions:** US East
   - **Alert Threshold:** 2 consecutive failures

### 2.4 Curriculum Endpoint Monitor

**Manual Setup:**
1. Navigate to Monitors → Uptime
2. Click "New Monitor"
3. Configure:
   - **Name:** Noni Curriculum
   - **Type:** HTTP
   - **URL:** `https://noni-api.fly.dev/api/v1/curriculum/units`
   - **Method:** GET
   - **Expected Status:** 200
   - **Check Interval:** 60 seconds
   - **Regions:** US East
   - **Alert Threshold:** 3 consecutive failures

---

## Step 3: Log Sources

### 3.1 Backend Logs (Fly.io)

**Manual Setup:**
1. Navigate to Logs → Sources
2. Click "Add Source"
3. Select "Fly.io"
4. Configure:
   - **Name:** noni-api-backend
   - **App:** noni-api
5. Configure log drain:

```bash
fly logs drain add betterstack \
  --app noni-api \
  --token <BETTERSTACK_TOKEN> \
  --format json
```

### 3.2 Frontend Logs (Cloudflare)

**Manual Setup:**
1. Navigate to Cloudflare Dashboard → Analytics & Logs → Logpush
2. Create new logpush job
3. Configure:
   - **Destination:** BetterStack
   - **Filter:** HTTP status >= 400
   - **Format:** JSON

---

## Step 4: Alert Configuration

### 4.1 Critical Alerts (SEV-1)

**Backend Down:**
1. Navigate to Monitors → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** Backend health monitor fails 2 consecutive checks
   - **Severity:** Critical
   - **Notify:** On-call primary, Engineering Lead, CEO
   - **Escalation:** 5 minutes without acknowledgment

**Auth Failure:**
1. Navigate to Monitors → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** Auth config monitor fails 2 consecutive checks
   - **Severity:** Critical
   - **Notify:** On-call primary, Engineering Lead
   - **Escalation:** 5 minutes without acknowledgment

### 4.2 Major Alerts (SEV-2)

**Frontend Down:**
1. Navigate to Monitors → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** Frontend monitor fails 3 consecutive checks
   - **Severity:** Major
   - **Notify:** On-call primary, Engineering Lead
   - **Escalation:** 15 minutes without acknowledgment

**Curriculum Degraded:**
1. Navigate to Monitors → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** Curriculum monitor fails 3 consecutive checks
   - **Severity:** Major
   - **Notify:** On-call primary
   - **Escalation:** 15 minutes without acknowledgment

### 4.3 Minor Alerts (SEV-3)

**High Error Rate:**
1. Navigate to Logs → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** Error rate > 1% for 5 minutes
   - **Severity:** Minor
   - **Notify:** Slack #alerts channel
   - **Escalation:** None

**High Latency:**
1. Navigate to Logs → Alerts
2. Create new alert rule
3. Configure:
   - **Trigger:** p99 latency > 500ms for 5 minutes
   - **Severity:** Minor
   - **Notify:** Slack #alerts channel
   - **Escalation:** None

---

## Step 5: Notification Channels

### 5.1 Slack Integration

**Setup:**
1. Navigate to Settings → Notifications
2. Add Slack workspace
3. Configure:
   - **Workspace:** Noni Engineering
   - **Channel:** #alerts (for SEV-3), #incidents (for SEV-1/SEV-2)
   - **Webhook URL:** Configure in BetterStack

### 5.2 Email Integration

**Setup:**
1. Navigate to Settings → Notifications
2. Add email recipient
3. Configure:
   - **Recipients:** help@noni.com
   - **Format:** Include incident details, severity, escalation path

### 5.3 SMS Integration

**Setup:**
1. Navigate to Settings → Notifications
2. Add SMS gateway
3. Configure:
   - **Recipients:** On-call primary phone numbers
   - **Triggers:** SEV-1 and SEV-2 only

---

## Step 6: Dashboard Setup

### 6.1 Operations Dashboard

**Setup:**
1. Navigate to Dashboards
2. Create new dashboard
3. Name: "Noni Operations"
4. Add widgets:
   - Backend uptime (last 24 hours)
   - Frontend uptime (last 24 hours)
   - Error rate graph (last 1 hour)
   - Latency p99 graph (last 1 hour)
   - Active incidents list
   - Recent alert history

### 6.2 Performance Dashboard

**Setup:**
1. Navigate to Dashboards
2. Create new dashboard
3. Name: "Noni Performance"
4. Add widgets:
   - Request latency distribution
   - Error rate by endpoint
   - Request count by endpoint
   - Database query performance
   - Circuit breaker state transitions

### 6.3 Clerk Telemetry Dashboard

**Setup:**
1. Navigate to Dashboards
2. Create new dashboard
3. Name: "Clerk Authentication"
4. Add widgets:
   - Widget load time graph
   - Sign-in success rate
   - Sign-in error rate
   - Sign-in abandonment rate
   - Authentication latency

---

## Step 7: Integration Verification

### 7.1 Verify Monitors

**Check:**
1. Navigate to Monitors → Uptime
2. Verify all 4 monitors are active
3. Check recent check results
4. Verify alert rules are configured

### 7.2 Verify Log Sources

**Check:**
1. Navigate to Logs → Sources
2. Verify backend log source is receiving logs
3. Verify log format is JSON
4. Check for recent log entries

### 7.3 Verify Alerts

**Check:**
1. Navigate to Monitors → Alerts
2. Verify alert rules are active
3. Test notification channels
4. Verify escalation paths

### 7.4 Verify Telemetry

**Check:**
1. Navigate to Dashboards
2. Verify Clerk telemetry dashboard is receiving data
3. Check widget load times
4. Verify error tracking

---

## Step 8: Environment Configuration

### 8.1 Backend Configuration

**Update .env:**
```bash
BETTERSTACK_API_KEY=your_api_key_here
BETTERSTACK_SOURCE_NAME=noni-api
```

**Update configuration:**
```bash
# Rebuild and deploy
cd backend
# Add environment variables
fly deploy
```

### 8.2 Frontend Configuration

**No configuration needed** - Clerk telemetry is integrated via backend API.

---

## Step 9: Testing

### 9.1 Monitor Testing

**Test Monitor:**
1. Temporarily stop Fly.io machine
2. Verify alert fires within expected time
3. Check notification delivery
4. Re-enable machine and verify recovery alert

### 9.2 Log Ingestion Testing

**Test Logs:**
1. Generate test traffic to the API
2. Verify logs appear in BetterStack within 30 seconds
3. Confirm JSON structure is correctly parsed
4. Test log search and filtering

### 9.3 Dashboard Testing

**Test Dashboards:**
1. Compare dashboard metrics with direct API checks
2. Verify real-time updates
3. Test time range selectors
4. Validate alert threshold calculations

---

## Troubleshooting

### Logs Not Appearing

**Issue:** Logs not appearing in BetterStack

**Solutions:**
1. Check Fly.io log drain status: `fly logs drains list --app noni-api`
2. Verify BetterStack token is valid
3. Check network connectivity between Fly.io and BetterStack
4. Review BetterStack log source configuration

### Alerts Not Firing

**Issue:** Alerts not firing

**Solutions:**
1. Verify monitor configuration is active
2. Check alert rule conditions
3. Confirm notification channel settings
4. Test notification delivery manually

### Metrics Not Scraping

**Issue:** Metrics not appearing

**Solutions:**
1. Verify `/metrics` endpoint is accessible
2. Check Prometheus source configuration
3. Review firewall rules
4. Test scraping with curl

---

## Maintenance

### Regular Tasks

**Weekly:**
- Review alert rules for false positives
- Check on-call schedule coverage
- Verify log ingestion rates

**Monthly:**
- Review BetterStack costs and usage
- Optimize alert thresholds based on data
- Update dashboard configurations as needed

**Quarterly:**
- Review BetterStack security settings
- Review and update contact information
- Test backup and recovery procedures

---

## Next Steps

After completing this quick start:

1. **Configure On-Call Schedule**
   - Set up on-call rotation in BetterStack
   - Add team members with contact information
   - Configure notification channels

2. **Implement Clerk Dashboard Configuration**
   - Disable unnecessary social login options
   - Separate sign-in and sign-up flows
   - Minimize form fields

3. **Run Load Tests**
   - Execute k6 load tests
   - Verify performance baselines
   - Check alert thresholds

---

## References

- BetterStack Documentation: https://betterstack.com/docs
- Fly.io Documentation: https://fly.io/docs
- Cloudflare Documentation: https://developers.cloudflare.com
- BetterStack Setup Guide: `docs/ops/betterstack-setup.md`
- Clerk Fallback Strategy: `docs/ops/clerk-fallback-strategy.md`

---

## Support

**BetterStack Support:** https://betterstack.com/support  
**Internal Contact:** help@noni.com