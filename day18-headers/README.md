# D18: Audit, Fix, Re-audit

**Lethabo Mashia** · BSc IT (Software Engineering), Eduvos Midrand · LITA programme, Day 18 (AI-guided lab)

## The problem
A default Flask site sends none of the browser security headers that block clickjacking, content sniffing, script injection impact and protocol downgrades. I audited a demo clinic site with my own [Security Header Auditor](../security-header-auditor/), fixed it with one `after_request` hook, and proved the fix with an audit, a test suite and a generated comparison table.

Why it matters in South Africa: clinic and booking sites handle patient data, and POPIA expects appropriate technical safeguards.

## Result
Scored by my Auditor (out of 100), same requests against both versions:

| Path | Status | Baseline | Hardened |
|---|---|---|---|
| `/` | 200 | 0/100 (Weak) | 100/100 (Strong) |
| `/about` | 200 | 0/100 (Weak) | 100/100 (Strong) |
| `/does-not-exist` | 404 | 0/100 (Weak) | 100/100 (Strong) |
| `/static/style.css` | 200 | 0/100 (Weak) | 100/100 (Strong) |

Raw Auditor output against the live servers: `baseline.txt` and `hardened.txt`. Tests: 9 passed.

## Design decisions
- **One `after_request` hook, policy as data.** It stamps every response, including 404s and static files, so no route can be forgotten. The headers live in a dictionary with a reason beside each, so a reviewer can read the whole policy in one place.
- **No `'unsafe-inline'`.** The CSP refuses inline code entirely, so the CSS lives in `/static/style.css`. A guard `assert` fails at start-up if inline code is ever allowed.
- **Proof, not claims.** `compare.py` scores the same requests against the baseline and hardened apps with my Auditor, so anyone can regenerate the table.

## What each header stops
| Header | What it stops |
|---|---|
| Content-Security-Policy | Limits what an injected script can do, and blocks framing |
| Strict-Transport-Security | Downgrade to HTTP on later visits |
| X-Content-Type-Options | A disguised upload being run as a script |
| X-Frame-Options | Clickjacking (older browsers) |
| Referrer-Policy | Leaking full page URLs to other sites |
| Permissions-Policy | Abuse of camera, microphone and location |

## HTTPS and HSTS
HTTP is readable and changeable by anyone on the network. HTTPS (TLS) adds encryption, tamper detection and proof of the server's identity. HSTS tells browsers to use HTTPS every time. On this local demo the HSTS header is present and my Auditor counts it, but browsers ignore it over plain HTTP, so it protects only once the site is served over HTTPS.

## What headers do NOT fix
They reduce the impact of flaws, they don't remove them. SQL injection, broken authentication and unescaped output still work with perfect headers. The very first visit can still be downgraded unless the site is on the HSTS preload list.

## Predictions vs reality
I committed `predictions.md` before writing any code.
- **Right:** a plain Flask app sends none of the six headers (0/100 on every path, including the 404), and `after_request` puts all six on every hardened response, 404 included (100/100).
- **Unsure, then confirmed:** I did not know whether my Auditor counts HSTS over plain HTTP. Reading `auditor.py` showed it checks presence only, and the hardened app scored 100/100.
- **Wrong:** I wrote my scores out of 6, but my Auditor scores out of 100. It is the same meaning (0/6 is 0/100). I also predicted 11 tests and the suite has 9, a counting slip. My first baseline audit ran before the server was up, so I re-ran it.

## Run it
    python day18-headers\app.py            # baseline, port 5000
    python day18-headers\secure_app.py     # hardened, port 5001
    python -m pytest day18-headers\test_headers.py -v
    python day18-headers/compare.py

## Files
`app.py` · `secure_app.py` · `test_headers.py` · `compare.py` · `before_after.md` · `baseline.txt` · `hardened.txt` · `predictions.md` (committed alone, before any code)