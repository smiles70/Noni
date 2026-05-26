/**
 * Sprint 27 SRE-C3: k6 load test baseline.
 *
 * Run: k6 run scripts/k6-smoke.js
 */
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // ramp up
    { duration: '5m', target: 50 },   // steady state
    { duration: '2m', target: 100 },  // ramp up
    { duration: '5m', target: 100 },  // steady state
    { duration: '2m', target: 200 },  // ramp up
    { duration: '5m', target: 200 },  // steady state
    { duration: '2m', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(99)<500'],
    http_req_failed: ['rate<0.001'],
  },
};

const BASE = __ENV.API_BASE_URL || 'https://noni-api.fly.dev';

export default function () {
  const urls = [
    `${BASE}/health`,
    `${BASE}/api/v1/curriculum/module-1/units`,
    `${BASE}/api/v1/auth/config`,
  ];

  for (const url of urls) {
    const res = http.get(url);
    check(res, {
      'status is 200 or 302': (r) => r.status === 200 || r.status === 302,
      'p99 < 500ms': (r) => r.timings.duration < 500,
    });
  }

  sleep(1);
}
