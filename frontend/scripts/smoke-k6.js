import http from "k6/http";
import { check } from "k6";

const url = __ENV.SMOKE_URL || "https://www.mynaani.com";

export const options = {
  vus: parseInt(__ENV.K6_VUS || "1", 10),
  duration: __ENV.K6_DURATION || "10s",
  thresholds: {
    http_req_duration: ["p(95)<500"],
    http_req_failed: ["rate<0.05"],
  },
};

export default function () {
  const res = http.get(url);
  check(res, {
    "status is 200": (r) => r.status === 200,
    "p95 latency under 500ms": () => res.timings.duration < 500,
  });
}
