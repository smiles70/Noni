/**
 * Agentic CI — Load Generator (k6)
 *
 * Sandboxed ramp-up against the local Vite dev server only. Does not target
 * production.
 */
import http from "k6/http";
import { check, sleep } from "k6";

const BASE = __ENV.STAGING_BASE_URL || "http://127.0.0.1:5173";

export const options = {
  stages: [
    { duration: "10s", target: 5 },
    { duration: "10s", target: 10 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.01"],
  },
};

const ROUTES = ["/", "/for-communities", "/signin"];

export default function () {
  for (const route of ROUTES) {
    const res = http.get(`${BASE}${route}`);
    check(res, {
      "status is 200": (r) => r.status === 200,
      "p95 < 500ms": (r) => r.timings.duration < 500,
    });
  }
  sleep(1);
}
