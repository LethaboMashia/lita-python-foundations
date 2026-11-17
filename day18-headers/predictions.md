# D18 Predictions: written before any code, audit or test run

Lethabo Mashia · LITA D18 · Audit, Fix, Re-audit
Written Tue 17 Nov 2026, before running anything. Committed alone, before any code.

## 1. Which of the six security headers does a plain Flask app send?
| Header | Sent by default? | Reasoning |
|---|---|---|
| Strict-Transport-Security | No | Flask never sets it, and browsers ignore it over plain HTTP anyway |
| X-Content-Type-Options | No | Opt-in. Flask sets only Content-Type, Content-Length and Date |
| X-Frame-Options | No | Opt-in. Framing protection must be switched on |
| Referrer-Policy | No | Not set, so the browser falls back to its own default |
| Permissions-Policy | No | Opt-in |
| Content-Security-Policy | No | Opt-in. Off by default so older sites keep working |

Prediction: 0 of 6.

## 2. The 404 page
Baseline: the 404 carries 0 of 6 security headers. A 404 is just another response, built by Flask with no security headers unless I add them.
Hardened: the 404 carries all six, because `after_request` runs on every response, error responses included.

## 3. Auditor scores (scale: headers present out of 6; edit if my Auditor differs)
- Baseline: 0/6 on `/` and 0/6 on the 404
- Hardened: 6/6 on `/` and 6/6 on the 404

## 4. Tests
7 pytest tests, all expected to pass first run.

## 5. What I am unsure about
- Whether my Auditor counts HSTS as present when served over plain HTTP. I expect it checks presence only, while a browser would ignore HSTS on HTTP.
- Whether `default-src 'self'` will block anything on my pages. I expect not, once the CSS lives in an external file.