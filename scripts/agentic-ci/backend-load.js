/**
 * Agentic CI — Backend Load & Latency Gate (k6)
 *
 * Targets the local sandbox started by backend-smoke-start.py.
 * Does not target production.
 */
import http from "k6/http";
import { check, sleep } from "k6";

const BASE = __ENV.STAGING_BASE_URL || "http://127.0.0.1:8000";

// Treat 302 (legacy redirect) and 429 (rate-limiter shedding) as expected.
http.setResponseCallback(http.expectedStatuses(200, 302, 429));

export const options = {
  stages: [
    { duration: "10s", target: 10 },
    { duration: "20s", target: 25 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};

export default function () {
  const health = http.get(`${BASE}/health`);
  check(health, {
    "health is 200": (r) => r.status === 200,
    "health p95 < 500ms": (r) => r.timings.duration < 500,
  });

  const landing = http.get(`${BASE}/api/v1/landing/page`);
  check(landing, {
    "landing is 200": (r) => r.status === 200,
    "landing p95 < 500ms": (r) => r.timings.duration < 500,
  });

  const menu = http.get(`${BASE}/api/v1/curriculum/menu`);
  check(menu, {
    "menu is 200 or 429": (r) => r.status === 200 || r.status === 429,
    "menu p95 < 500ms": (r) => r.timings.duration < 500,
  });

  sleep(1);
}
