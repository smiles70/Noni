/**
 * Noni Load Test — k6 curriculum endpoint baseline
 *
 * Run locally against the docker-compose stack:
 *   k6 run --env API_BASE=http://localhost:8000 tests/load/k6-curriculum.js
 *
 * Run against staging/production:
 *   k6 run --env API_BASE=https://noni-api.fly.dev tests/load/k6-curriculum.js
 *
 * Target: validate 100 concurrent users (soft-launch ceiling).
 * SLOs: p99 latency < 500ms, error rate < 0.1%
 */

import http from 'k6/http';
import { check, sleep } from 'k6';

const API_BASE = __ENV.API_BASE || 'http://localhost:8000';

export const options = {
  // 100 concurrent users = soft-launch ceiling.
  stages: [
    { duration: '2m', target: 25 },   // warm-up
    { duration: '3m', target: 50 },   // ramp to 50
    { duration: '3m', target: 100 },  // ramp to 100
    { duration: '5m', target: 100 },  // steady state
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],   // p99 under 500ms
    http_req_failed: ['rate<0.001'],    // error rate under 0.1%
  },
};

export default function () {
  // Realistic user journey: hit health, then a curriculum page.
  const healthRes = http.get(`${API_BASE}/health`);
  check(healthRes, { 'health status 200': (r) => r.status === 200 });

  sleep(Math.random() * 2 + 1); // 1–3s think time

  const curriculumRes = http.get(`${API_BASE}/api/curriculum/units`);
  check(curriculumRes, {
    'curriculum status 200': (r) => r.status === 200,
    'curriculum response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(Math.random() * 3 + 2); // 2–5s think time before next interaction
}
