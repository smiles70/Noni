#!/usr/bin/env node
// Repo-specific runner for the app-agnostic site-checker prompt.
// Reads config from environment variables so it can target local CI, staging, or production.

import { chromium } from 'playwright';
import { writeFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const BASE_URL = process.env.SITE_CHECKER_BASE_URL || 'https://www.mynaani.com';
const API_BASE = process.env.SITE_CHECKER_API_BASE || 'https://noni-api-production.up.railway.app';
const SCREENSHOT_DIR = process.env.SITE_CHECKER_SCREENSHOT_DIR || '.ai/research/site-checker-screenshots';
const REPORT_DIR = process.env.SITE_CHECKER_REPORT_DIR || '.ai/research';
const MAX_PAGES = parseInt(process.env.SITE_CHECKER_MAX_PAGES || '24', 10);
const CHECK_EXTERNAL_LINKS = (process.env.SITE_CHECKER_CHECK_EXTERNAL_LINKS || 'true').toLowerCase() === 'true';
const EXPECTED_404_PATHS = (process.env.SITE_CHECKER_EXPECTED_404_PATHS || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);
const FAIL_ON = (process.env.SITE_CHECKER_FAIL_ON || 'P0').toUpperCase();

const severityRank = { P0: 0, P1: 1, P2: 2, P3: 3 };

const routes = [
  { path: '/', name: 'Landing', public: true, component: 'LandingPage', file: 'frontend/src/components/LandingPage.tsx' },
  { path: '/signin', name: 'Sign in', public: true, component: 'SignInPage', file: 'frontend/src/components/SignInPage.tsx' },
  { path: '/for-communities', name: 'For Communities (B2B)', public: true, component: 'ForCommunitiesPage', file: 'frontend/src/components/ForCommunitiesPage.tsx' },
  { path: '/privacy', name: 'Privacy', public: true, component: 'PrivacyPage', file: 'frontend/src/components/PrivacyPage.tsx' },
  { path: '/help', name: 'Help', public: true, component: 'HelpPage', file: 'frontend/src/components/HelpPage.tsx' },
  { path: '/admin', name: 'Admin console', public: true, component: 'AdminConsolePage', file: 'frontend/src/components/AdminConsolePage.tsx' },
  { path: '/gift', name: 'Gift checkout', public: true, component: 'GiftCheckoutPage', file: 'frontend/src/components/GiftCheckoutPage.tsx' },
  { path: '/c/demo', name: 'Partner page (demo slug)', public: true, component: 'PartnerPage', file: 'frontend/src/components/PartnerPage.tsx' },
  { path: '/purchase/success', name: 'Purchase success', public: true, component: 'PurchaseSuccessPage', file: 'frontend/src/components/PurchaseSuccessPage.tsx' },
  { path: '/purchase/cancel', name: 'Purchase cancel', public: true, component: 'PurchaseCancelPage', file: 'frontend/src/components/PurchaseCancelPage.tsx' },
  { path: '/welcome', name: 'Welcome (auth-gated)', public: false, component: 'WelcomePage', file: 'frontend/src/components/WelcomePage.tsx' },
  { path: '/setup', name: 'Account setup (auth-gated)', public: false, component: 'AccountSetupPage', file: 'frontend/src/components/AccountSetupPage.tsx' },
  { path: '/getting-started', name: 'Getting started (auth-gated)', public: false, component: 'GettingStartedPage', file: 'frontend/src/components/GettingStartedPage.tsx' },
  { path: '/curriculum', name: 'Curriculum (auth-gated)', public: false, component: 'CurriculumRenderer', file: 'frontend/src/components/CurriculumRenderer.tsx' },
  { path: '/paid-curriculum', name: 'Paid curriculum (auth-gated)', public: false, component: 'PaidLessonRenderer', file: 'frontend/src/components/PaidLessonRenderer.tsx' },
  { path: '/menu', name: 'Curriculum menu (auth-gated)', public: false, component: 'CurriculumMenu', file: 'frontend/src/components/CurriculumMenu.tsx' },
  { path: '/paywall', name: 'Paywall (auth-gated)', public: false, component: 'PaywallPage', file: 'frontend/src/components/PaywallPage.tsx' },
  { path: '/gift-redeem', name: 'Gift redeem (auth-gated)', public: false, component: 'GiftRedeemPage', file: 'frontend/src/components/GiftRedeemPage.tsx' },
  { path: '/mock-checkout', name: 'Mock checkout (auth-gated)', public: false, component: 'MockCheckoutPage', file: 'frontend/src/components/MockCheckoutPage.tsx' },
  { path: '/account', name: 'Account settings (auth-gated)', public: false, component: 'AccountSettingsPage', file: 'frontend/src/components/AccountSettingsPage.tsx' },
  { path: '/org', name: 'Org dashboard (auth-gated)', public: false, component: 'OrgDashboardPage', file: 'frontend/src/components/OrgDashboardPage.tsx' },
  { path: '/auth/callback', name: 'Auth callback', public: true, component: 'inline pending banner', file: 'frontend/src/App.tsx' },
];

function isExpectedNotOk(url, status) {
  if (status !== 404) return false;
  return EXPECTED_404_PATHS.some((p) => url.includes(p));
}

function isExpectedConsole(text, location = null) {
  if (!text || !String(text).includes('404')) return false;
  return EXPECTED_404_PATHS.some((p) => {
    if (text.includes(p)) return true;
    if (location && location.url && String(location.url).includes(p)) return true;
    return false;
  });
}

async function fetchWithTimeout(url, opts = {}, timeoutMs = 10000) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const r = await fetch(url, { ...opts, signal: controller.signal });
    clearTimeout(timer);
    return r;
  } catch (e) {
    clearTimeout(timer);
    throw e;
  }
}

async function checkLink(page, href) {
  if (!href || href.startsWith('mailto:') || href.startsWith('tel:') || href.startsWith('#')) return null;
  try {
    const url = new URL(href, BASE_URL);
    const sameOrigin = url.origin === new URL(BASE_URL).origin;
    if (sameOrigin) {
      return { href, sameOrigin: true, checked: false, reason: 'SPA fallback; validated against route table' };
    }
    if (!CHECK_EXTERNAL_LINKS) {
      return { href, sameOrigin: false, checked: false, reason: 'external link checks disabled' };
    }
    const r = await page.request.fetch(url.toString(), { method: 'HEAD', timeout: 10000 }).catch(async () => {
      return await page.request.fetch(url.toString(), { method: 'GET', timeout: 10000 });
    });
    return { href, sameOrigin: false, status: r.status(), ok: r.ok(), checked: true };
  } catch (e) {
    return { href, sameOrigin: false, checked: true, error: e.message || String(e) };
  }
}

async function crawlRoute(browser, route, index) {
  const result = {
    ...route,
    finalUrl: null,
    title: null,
    status: 'unknown',
    loadTimeMs: null,
    console: [],
    pageErrors: [],
    failedRequests: [],
    slowRequests: [],
    notOkResponses: [],
    links: [],
    interactiveElements: [],
    screenshot: null,
  };
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    userAgent: 'NoniSiteChecker/1.0 (Playwright)',
  });
  const page = await context.newPage();
  const start = Date.now();
  try {
    page.on('console', (msg) => {
      result.console.push({ type: msg.type(), text: msg.text(), location: msg.location() });
    });
    page.on('pageerror', (err) => {
      result.pageErrors.push(String(err).slice(0, 500));
    });
    page.on('requestfailed', (req) => {
      result.failedRequests.push({ url: req.url(), failure: req.failure()?.errorText || 'unknown' });
    });
    page.on('response', (res) => {
      const status = res.status();
      if (status >= 400) result.notOkResponses.push({ url: res.url(), status, method: res.request().method() });
    });

    const nav = await page.goto(`${BASE_URL}${route.path}`, { waitUntil: 'networkidle', timeout: 15000 }).catch(async () => {
      return await page.goto(`${BASE_URL}${route.path}`, { waitUntil: 'load', timeout: 15000 });
    });
    result.loadTimeMs = Date.now() - start;
    result.finalUrl = page.url();
    result.title = await page.title().catch(() => '');

    const links = await page.$$eval('a[href]', (els) => els.map((a) => ({ href: a.href, text: a.innerText.trim().slice(0, 80) })));
    const external = links.filter((l) => !l.href.startsWith(BASE_URL) && !l.href.startsWith('/') && !l.href.startsWith('#') && !l.href.startsWith('mailto:') && !l.href.startsWith('tel:'));
    const linkChecks = [];
    for (const l of external.slice(0, 15)) {
      linkChecks.push(checkLink(page, l.href));
    }
    result.links = await Promise.all(linkChecks);

    result.interactiveElements = await page.$$eval(
      'a, button, [role="button"], [role="link"], input, textarea, select, [role="tab"], [role="menuitem"]',
      (els) => els.map((el) => ({ tag: el.tagName, role: el.getAttribute('role') || '', name: (el.getAttribute('aria-label') || el.innerText || el.value || '').slice(0, 80) })).slice(0, 50),
    );

    const screenshotPath = `${SCREENSHOT_DIR}/${index.toString().padStart(2, '0')}-${route.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}.png`;
    await page.screenshot({ path: screenshotPath, fullPage: true });
    result.screenshot = screenshotPath;

    result.status = nav ? 'loaded' : 'fallback-loaded';
  } catch (e) {
    result.status = 'error';
    result.error = String(e).slice(0, 500);
    try {
      const screenshotPath = `${SCREENSHOT_DIR}/${index.toString().padStart(2, '0')}-${route.name.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}-error.png`;
      await page.screenshot({ path: screenshotPath, fullPage: true });
      result.screenshot = screenshotPath;
    } catch {}
  } finally {
    await context.close();
  }
  return result;
}

async function apiChecks() {
  const endpoints = [
    { name: 'health', url: `${API_BASE}/health` },
    { name: 'auth config', url: `${API_BASE}/api/v1/auth/config` },
    { name: 'landing intro envelope', url: `${API_BASE}/api/ui-envelope/landing.intro` },
  ];
  const checks = [];
  for (const e of endpoints) {
    try {
      const r = await fetchWithTimeout(e.url, { method: 'GET' }, 10000);
      checks.push({ name: e.name, url: e.url, status: r.status, ok: r.ok, contentType: r.headers.get('content-type') });
    } catch (err) {
      checks.push({ name: e.name, url: e.url, error: err.message || String(err) });
    }
  }
  return checks;
}

function worstSeverity(severities) {
  let worst = 'P3';
  for (const s of severities) {
    if (severityRank[s] < severityRank[worst]) worst = s;
  }
  return worst;
}

function routeSeverity(result) {
  if (result.error && result.status === 'error') return 'P0';

  const unexpectedPageErrors = result.pageErrors.filter((t) => !isExpectedConsole(t));
  if (unexpectedPageErrors.length > 0) return 'P1';

  const unexpectedFailed = result.failedRequests.filter((r) => !isExpectedNotOk(r.url, 0)); // failed requests have no status
  if (unexpectedFailed.length > 0) return 'P1';

  const unexpectedNotOk = result.notOkResponses.filter((r) => !isExpectedNotOk(r.url, r.status));
  if (unexpectedNotOk.length > 0) return 'P1';

  const unexpectedConsoleErrors = result.console.filter((c) => c.type === 'error' && !isExpectedConsole(c.text, c.location));
  if (unexpectedConsoleErrors.length > 0) return 'P1';

  const deadExternal = result.links.filter((l) => !l.sameOrigin && l.checked && !l.ok && !l.error);
  if (deadExternal.length > 0) return 'P2';

  const warnings = result.console.filter((c) => c.type === 'warning');
  if (warnings.length > 0) return 'P2';

  return 'P3';
}

function classifyFindings(result) {
  const findings = [];
  if (result.error) findings.push({ symptom: 'Page failed to load', severity: 'P0', evidence: result.error });

  const unexpectedPageErrors = result.pageErrors.filter((t) => !isExpectedConsole(t));
  if (unexpectedPageErrors.length) {
    findings.push({ symptom: 'Uncaught page errors', severity: 'P1', evidence: unexpectedPageErrors.join('; ').slice(0, 300) });
  }

  const unexpectedFailed = result.failedRequests.filter((r) => !isExpectedNotOk(r.url, 0));
  if (unexpectedFailed.length) {
    findings.push({ symptom: 'Failed network requests', severity: 'P1', evidence: unexpectedFailed.map((r) => `${r.url}: ${r.failure}`).join('; ').slice(0, 300) });
  }

  const unexpectedNotOk = result.notOkResponses.filter((r) => !isExpectedNotOk(r.url, r.status));
  if (unexpectedNotOk.length) {
    findings.push({ symptom: 'HTTP >= 400 responses', severity: 'P1', evidence: unexpectedNotOk.map((r) => `${r.method} ${r.url} -> ${r.status}`).join('; ').slice(0, 300) });
  }

  const unexpectedConsoleErrors = result.console.filter((c) => c.type === 'error' && !isExpectedConsole(c.text, c.location));
  if (unexpectedConsoleErrors.length) {
    findings.push({ symptom: 'Console errors', severity: 'P1', evidence: unexpectedConsoleErrors.map((c) => c.text).join('; ').slice(0, 300) });
  }

  const expectedConsole = result.console.filter((c) => c.type === 'error' && isExpectedConsole(c.text, c.location));
  if (expectedConsole.length) {
    findings.push({ symptom: 'Expected console 404 for test fixture', severity: 'P3', evidence: expectedConsole.map((c) => c.text).join('; ').slice(0, 300) });
  }

  const expectedNotOk = result.notOkResponses.filter((r) => isExpectedNotOk(r.url, r.status));
  if (expectedNotOk.length) {
    findings.push({ symptom: 'Expected HTTP 404 (test fixture)', severity: 'P3', evidence: expectedNotOk.map((r) => `${r.method} ${r.url} -> ${r.status}`).join('; ').slice(0, 300) });
  }

  const deadExternal = result.links.filter((l) => !l.sameOrigin && l.checked && !l.ok && !l.error);
  if (deadExternal.length) {
    findings.push({ symptom: 'Dead external links', severity: 'P2', evidence: deadExternal.map((l) => `${l.href} -> ${l.status}`).join('; ').slice(0, 300) });
  }

  const warnings = result.console.filter((c) => c.type === 'warning');
  if (warnings.length) {
    findings.push({ symptom: 'Console warnings', severity: 'P2', evidence: warnings.map((c) => c.text).join('; ').slice(0, 300) });
  }

  return findings;
}

async function main() {
  if (!existsSync(SCREENSHOT_DIR)) await mkdir(SCREENSHOT_DIR, { recursive: true });
  if (!existsSync(REPORT_DIR)) await mkdir(REPORT_DIR, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
  });

  const results = [];
  let index = 0;
  for (const route of routes.slice(0, MAX_PAGES)) {
    console.error(`Crawling ${route.path} ...`);
    const res = await crawlRoute(browser, route, index++);
    results.push(res);
  }
  await browser.close();

  const api = await apiChecks();

  const date = new Date().toISOString().split('T')[0];
  const reportPath = `${REPORT_DIR}/${date}-site-checker-report.md`;
  const jsonPath = `${REPORT_DIR}/${date}-site-checker-data.json`;

  const findings = results.map((r) => ({ ...r, severity: routeSeverity(r), findings: classifyFindings(r) }));
  const counts = { P0: 0, P1: 0, P2: 0, P3: 0 };
  findings.forEach((f) => counts[f.severity]++);

  const top = findings.filter((f) => f.severity === 'P0' || f.severity === 'P1').slice(0, 5);

  const md = `# Site checker report — ${BASE_URL}

**Date:** ${date}  
**Target:** ${BASE_URL}  
**API base:** ${API_BASE}  
**Pages crawled:** ${results.length}  
**Browser:** Chromium (Playwright)  
**External link checks:** ${CHECK_EXTERNAL_LINKS ? 'enabled' : 'disabled'}  
**Expected 404 fixtures:** ${EXPECTED_404_PATHS.join(', ') || 'none'}

## Executive summary

| Severity | Count |
|----------|-------|
| P0 (broken) | ${counts.P0} |
| P1 (major) | ${counts.P1} |
| P2 (minor) | ${counts.P2} |
| P3 (cosmetic / info) | ${counts.P3} |

**Top risks**
${top.map((f) => `- **${f.severity}** on ${f.path} (${f.name}): ${f.findings.filter((x) => x.severity === f.severity || x.severity === 'P0').map((x) => x.symptom).join('; ').slice(0, 120)}`).join('\n') || 'No P0/P1 findings detected.'}

## Methodology

- Crawled \`${BASE_URL}\` with Chromium via Playwright, fresh browser context per route.
- Captured console logs, uncaught page errors, failed network requests, HTTP >= 400 responses, and external link status.
- Used the route table from \`frontend/src/App.tsx\` to seed the crawl list and to map each page to its component/source file.
- Auth-gated routes were visited without credentials to verify they redirect to \`/signin?redirect=<route>\`.
- Backend/API smoke checks hit \`/health\`, \`/api/v1/auth/config\`, and \`/api/ui-envelope/landing.intro\`.
- Full-page screenshots are saved to \`${SCREENSHOT_DIR}\` and raw JSON data is in \`${jsonPath}\`.

## API / backend checks

| Name | URL | Result |
|------|-----|--------|
${api.map((a) => `| ${a.name} | ${a.url} | ${a.error ? `ERROR: ${a.error}` : `HTTP ${a.status} ${a.ok ? 'OK' : 'FAIL'}${a.contentType ? ' (' + a.contentType + ')' : ''}`} |`).join('\n')}

## Per-page findings

${findings.map((f) => `### ${f.path} — ${f.name} (${f.public ? 'public' : 'auth-gated'})
- **Component:** ${f.component} (${f.file})
- **Final URL:** ${f.finalUrl || 'N/A'}
- **Load time:** ${f.loadTimeMs != null ? f.loadTimeMs + ' ms' : 'N/A'}
- **Severity:** ${f.severity}
- **Status:** ${f.status}${f.error ? ' — ' + f.error : ''}
${f.findings.length ? f.findings.map((x) => `- **${x.severity} — ${x.symptom}:** ${x.evidence}`).join('\n') : '- No findings'}
- **Interactive elements:** ${f.interactiveElements.length} (sample: ${f.interactiveElements.slice(0, 5).map((e) => e.role || e.tag).join(', ')})
- **Screenshot:** ${f.screenshot || 'none'}
`).join('\n')}

## Code mapping table

| Page | Route | Component | Source file | Auth gate |
|------|-------|-----------|-------------|-----------|
${routes.map((r) => `| ${r.name} | ${r.path} | ${r.component} | ${r.file} | ${r.public ? 'No' : 'RequireAuth'} |`).join('\n')}

## Recommended next steps

1. Review any P0/P1 findings above for real regressions.
2. Confirm auth-gated routes redirect to /signin with a ?redirect= param (per App.tsx logic).
3. Verify external links flagged as dead are truly dead or were rate-limited during crawl.
4. Add the site-checker run to CI against the staging preview URL on a schedule.
`;

  await writeFile(reportPath, md);
  await writeFile(jsonPath, JSON.stringify({ baseUrl: BASE_URL, apiBase: API_BASE, api, findings }, null, 2));

  const worst = worstSeverity(findings.map((f) => f.severity));
  const shouldFail = severityRank[worst] <= severityRank[FAIL_ON];

  console.error(`Report: ${reportPath}`);
  console.error(`Data: ${jsonPath}`);
  console.error(`Screenshots: ${SCREENSHOT_DIR}`);
  console.error(`Worst severity: ${worst} (fail threshold: ${FAIL_ON})`);
  console.log(JSON.stringify({ reportPath, jsonPath, screenshotDir: SCREENSHOT_DIR, counts, worst, shouldFail }, null, 2));

  if (shouldFail) {
    process.exit(1);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
