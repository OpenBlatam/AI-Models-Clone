import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  thresholds: {
    http_req_duration: ['p(95)<600'],
    http_req_failed: ['rate<0.02'],
  },
  stages: [
    { duration: '30s', target: 25 },
    { duration: '1m', target: 100 },
    { duration: '1m', target: 200 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const url = __ENV.API_URL || 'http://localhost:8080/v1/infer';
  const payload = JSON.stringify({ model: 'gpt2', prompt: 'hello world' });
  const params = { headers: { 'Content-Type': 'application/json' } };
  const res = http.post(url, payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}





