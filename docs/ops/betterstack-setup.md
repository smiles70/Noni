> **Deprecated:** legacy platform retired; production runs on Railway.

# BetterStack Monitoring Setup

**Version:** 1.0.0  
**Owner:** SRE / Platform Engineering  
**Last Updated:** 2026-08-08

---

## Overview

BetterStack provides unified monitoring, uptime monitoring, and alerting for the Mynaani platform. This guide covers the complete setup and configuration process.

---

## Prerequisites

- BetterStack account (https://betterstack.com)
- railway.app CLI installed and authenticated
- Mynaani backend deployed to railway.app
- Mynaani frontend deployed to Cloudflare Pages

---

## 1. Uptime Monitors

### 1.1 Backend Health Monitor

**Purpose:** Monitor the FastAPI backend health endpoint

**Configuration:**
- **Name:** Mynaani API Health
- **Type:** HTTP
- **URL:** `https://noni-api-production.up.railway.app/health`
- **Request Method:** GET
- **Expected Status Code:** 200
- **Check Interval:** 30 seconds
- **Regions:** US East, US West, EU West
- **Alert Threshold:** 2 consecutive failures

**Verification:**
```bash
curl -I https://noni-api-production.up.railway.app/health
# Expected: HTTP/2 200
```

### 1.2 Frontend Availability Monitor

**Purpose:** Monitor the Cloudflare Pages frontend

**Configuration:**
- **Name:** Mynaani Frontend
- **Type:** HTTP
- **URL:** `https://noni-web.pages.dev`
- **Request Method:** GET
- **Expected Status Code:** 200
- **Check Interval:** 60 seconds
- **Regions:** US East, US West, EU West
- **Alert Threshold:** 3 consecutive failures

**Verification:**
```bash
curl -I https://noni-web.pages.dev
# Expected: HTTP/2 200
```

### 1.3 Auth Endpoint Monitor

**Purpose:** Monitor authentication endpoint availability

**Configuration:**
- **Name:** Mynaani Auth Config
- **Type:** HTTP
- **URL:** `https://noni-api-production.up.railway.app/api/v1/auth/config`
- **Request Method:** GET
- **Expected Status Code:** 200
- **Check Interval:** 60 seconds
- **Regions:** US East
- **Alert Threshold:** 2 consecutive failures

### 1.4 Curriculum Endpoint Monitor

**Purpose:** Monitor core curriculum functionality

**Configuration:**
- **Name:** Mynaani Curriculum
- **Type:** HTTP
- **URL:** `https://noni-api-production.up.railway.app/api/v1/curriculum/units`
- **Request Method:** GET
- **Expected Status Code:** 200
- **Check Interval:** 60 seconds
- **Regions:** US East
- **Alert Threshold:** 3 consecutive failures

---

## 2. Log Source Integration

### 2.1 Backend Logs

**Purpose:** Collect structured JSON logs from FastAPI backend

**Setup Steps:**

1. **Create Log Source in BetterStack:**
   - Navigate to Logs > Sources
   - Click "Add Source"
   - Select "railway.app"
   - Name: `noni-api-backend`

2. **Configure railway.app Integration:**
   ```bash
   # Install BetterStack agent on railway.app
   railway scale count 0 --app noni-api
   railway deploy --remote-only
   
   # Add BetterStack log drain
   railway logs drain add betterstack \
     --app noni-api \
     --token <BETTERSTACK_TOKEN> \
     --format json
   ```

3. **Verify Log Ingestion:**
   - Check BetterStack Logs dashboard
   - Verify logs appear with correct JSON structure
   - Confirm request_id, path, status, latency_ms fields present

### 2.2 Frontend Logs

**Purpose:** Collect frontend error logs (optional for Cloudflare Pages)

**Setup Steps:**

1. **Create Log Source:**
   - Navigate to Logs > Sources
   - Click "Add Source"
   - Select "Cloudflare"
   - Name: `noni-frontend`

2. **Configure Cloudflare Integration:**
   - Navigate to Cloudflare Dashboard > Analytics & Logs > Logpush
   - Create new logpush job to BetterStack endpoint
   - Filter for HTTP status >= 400

---

## 3. Alert Configuration

### 3.1 On-Call Schedule

**Setup Steps:**

1. **Create On-Call Schedule:**
   - Navigate to Incidents > Schedules
   - Create schedule: `noni-on-call-primary`
   - Add team members with contact information
   - Set rotation: weekly with handoff on Monday 9:00 UTC

2. **Contact Information:**
   - Primary: help@noni.com
   - SMS: Configure SMS gateway integration
   - Voice: Configure phone call integration
   - Slack: Configure Slack workspace integration

### 3.2 Alert Rules

**Critical Alerts (SEV-1):**

1. **Backend Down**
   - Trigger: Backend health monitor fails 2 consecutive checks
   - Severity: Critical
   - Notify: On-call primary, Engineering Lead, CEO
   - Escalation: 5 minutes without acknowledgment

2. **Auth Failure**
   - Trigger: Auth config monitor fails 2 consecutive checks
   - Severity: Critical
   - Notify: On-call primary, Engineering Lead
   - Escalation: 5 minutes without acknowledgment

**Major Alerts (SEV-2):**

3. **Frontend Down**
   - Trigger: Frontend monitor fails 3 consecutive checks
   - Severity: Major
   - Notify: On-call primary, Engineering Lead
   - Escalation: 15 minutes without acknowledgment

4. **Curriculum Degraded**
   - Trigger: Curriculum monitor fails 3 consecutive checks
   - Severity: Major
   - Notify: On-call primary
   - Escalation: 15 minutes without acknowledgment

**Minor Alerts (SEV-3):**

5. **High Error Rate**
   - Trigger: Error rate > 1% for 5 minutes
   - Severity: Minor
   - Notify: Slack #alerts channel
   - No escalation required

6. **High Latency**
   - Trigger: p99 latency > 500ms for 5 minutes
   - Severity: Minor
   - Notify: Slack #alerts channel
   - No escalation required

### 3.3 Notification Channels

**Slack Integration:**
- Workspace: Mynaani Engineering
- Channel: #alerts (for SEV-3), #incidents (for SEV-1/SEV-2)
- Webhook URL: Configure in BetterStack notification settings

**Email Integration:**
- Recipients: help@noni.com
- Format: Include incident details, severity, and escalation path

**SMS Integration:**
- Provider: Configure SMS gateway
- Recipients: On-call primary phone numbers
- Triggers: SEV-1 and SEV-2 only

---

## 4. Dashboard Configuration

### 4.1 Operations Dashboard

**Purpose:** Single pane of glass for system health

**Components:**
- Backend uptime (last 24 hours)
- Frontend uptime (last 24 hours)
- Error rate graph (last 1 hour)
- Latency p99 graph (last 1 hour)
- Active incidents list
- Recent alert history

### 4.2 Performance Dashboard

**Purpose:** Track performance metrics over time

**Components:**
- Request latency distribution
- Error rate by endpoint
- Request count by endpoint
- Database query performance
- Circuit breaker state transitions

### 4.3 Business Metrics Dashboard

**Purpose:** Track user-facing metrics

**Components:**
- Active users (last 24 hours)
- Curriculum completion rate
- Auth success rate
- Checkout success rate
- Average session duration

---

## 5. Integration with Existing Infrastructure

### 5.1 Prometheus Metrics

**BetterStack can scrape Prometheus metrics:**

1. **Configure Prometheus Scraping:**
   - Navigate to Metrics > Sources
   - Add Prometheus source
   - URL: `https://noni-api-production.up.railway.app/metrics`
   - Scrape interval: 30 seconds

2. **Key Metrics to Monitor:**
   - `noni_http_requests_total` - Request count by path and status
   - `noni_request_latency_seconds` - Request latency by path
   - `noni_auth_session_outcomes_total` - Auth session outcomes
   - `noni_circuit_breaker_state_transitions_total` - Circuit breaker transitions

### 5.2 Custom Metrics

**Add custom metrics for business logic:**

```python
# In backend/app/telemetry.py
from prometheus_client import Counter

curriculum_completions = Counter(
    "noni_curriculum_completions_total",
    "Curriculum unit completions",
    ["module", "unit"]
)
```

---

## 6. Testing and Verification

### 6.1 Alert Testing

**Test Alert Delivery:**
1. Temporarily disable a railway.app machine
2. Verify alert fires within expected time
3. Confirm notification delivery to all channels
4. Re-enable machine and verify recovery alert

### 6.2 Log Ingestion Testing

**Test Log Collection:**
1. Generate test traffic to the API
2. Verify logs appear in BetterStack within 30 seconds
3. Confirm JSON structure is correctly parsed
4. Test log search and filtering

### 6.3 Dashboard Testing

**Test Dashboard Accuracy:**
1. Compare dashboard metrics with direct API checks
2. Verify real-time updates
3. Test time range selectors
4. Validate alert threshold calculations

---

## 7. Maintenance

### 7.1 Regular Tasks

**Weekly:**
- Review alert rules for false positives
- Check on-call schedule coverage
- Verify log ingestion rates

**Monthly:**
- Review and update contact information
- Optimize alert thresholds based on data
- Update dashboard configurations as needed

**Quarterly:**
- Review BetterStack costs and usage
- Evaluate additional monitoring needs
- Update documentation

### 7.2 Troubleshooting

**Logs Not Appearing:**
1. Check railway.app log drain status: `railway logs drains list --app noni-api`
2. Verify BetterStack token is valid
3. Check network connectivity between railway.app and BetterStack
4. Review BetterStack log source configuration

**Alerts Not Firing:**
1. Verify monitor configuration is active
2. Check alert rule conditions
3. Confirm notification channel settings
4. Test notification delivery manually

**Metrics Not Scraping:**
1. Verify `/metrics` endpoint is accessible
2. Check Prometheus source configuration
3. Review firewall rules
4. Test scraping with curl

---

## 8. Security Considerations

### 8.1 Access Control

- Restrict BetterStack dashboard access to authorized team members
- Use SSO integration if available
- Implement role-based access control
- Regular audit of user access

### 8.2 Data Privacy

- Ensure logs do not contain PII
- Configure log retention policies
- Use secure communication channels
- Encrypt sensitive data in transit

### 8.3 Secret Management

- Store BetterStack API tokens securely
- Rotate tokens quarterly
- Use environment variables for configuration
- Never commit tokens to version control

---

## 9. Cost Optimization

### 9.1 Monitoring Usage

- Optimize check intervals based on criticality
- Use regional monitoring strategically
- Review log volume and retention policies
- Implement log sampling for high-volume endpoints

### 9.2 Alert Optimization

- Consolidate similar alerts
- Use alert grouping to reduce noise
- Implement smart alerting based on patterns
- Regular review of alert effectiveness

---

## 10. References

- BetterStack Documentation: https://betterstack.com/docs
- railway.app Logging: https://railway.app/docs/observability/logging
- Cloudflare Logpush: https://developers.cloudflare.com/logs/get-started
- Incident Response Runbook: `docs/ops/incident-response-runbook.md`
- Recovery Runbook: `docs/ops/recovery-runbook.md`

---

## 11. Support

**BetterStack Support:** https://betterstack.com/support  
**Internal Contact:** help@noni.com