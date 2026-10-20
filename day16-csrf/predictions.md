# Predictions — Day 16: Cross-Site Request Forgery (CSRF)
*Hypotheses written before execution, per the carry-forward prediction habit.*

## Why CSRF Is Worth Taking Seriously
CSRF is dangerous precisely because it doesn't exploit a bug in the traditional sense — the server, the login system, and the session handling can all be working *exactly as designed*, and the attack still succeeds. It exploits a trust assumption baked into how cookies work by default: a browser attaches a site's cookies to a request regardless of which page or domain actually triggered that request. The vulnerability isn't "broken code," it's "code that correctly does what cookies were designed to do, in a context where that design is actively dangerous."

## Prediction 1 — Attacking `vulnerable_bank.py` with `evil_page.html`

**What I expect to happen:**
Once I'm logged into the bank app in one tab, my browser holds a valid session cookie for `127.0.0.1:5000`. If I then open `evil_page.html` — a completely unrelated, attacker-controlled file — in a second tab, I expect its hidden auto-submitting form to fire a POST request to `/transfer` the instant the page loads, with no click, no confirmation, and no visual indication anything happened.

**Why I expect it to succeed specifically on this app:** The `/transfer` route only checks `if "user" not in session` — it has no mechanism to verify that the request *intended* to come from the bank's own dashboard form versus any other page on the internet that happens to know the endpoint URL and parameter names. Since the browser attaches the session cookie automatically to any request sent to `127.0.0.1:5000`, regardless of which page initiated it, the server has no way to distinguish "Lethabo clicked Transfer on my dashboard" from "Lethabo's browser was tricked into submitting a form hosted somewhere else." I expect the balance on `/dashboard` to drop by R9999 and the terminal log to show a transfer to `attacker` that I never authorized.

## Prediction 2 — Defending with `secure_bank.py`

**What I expect to happen:**
The identical `evil_page.html` attack, re-run against the fixed server, should fail — ideally with a 403 Forbidden response — and the balance should remain untouched.

**Why I expect each specific defense to contribute:**
- **CSRF token:** The attacker's static HTML file has no way to know the per-session token value embedded in the bank's own form, since that token is generated server-side and only ever rendered inside the authenticated dashboard page. Without it, the server should reject the request outright.
- **SameSite=Lax cookie:** Even if the attacker somehow guessed or stole the token, a `SameSite=Lax` cookie is withheld by the browser on cross-site POST requests by default — meaning the session cookie itself wouldn't even be attached to the attacker's request, so the server would see an unauthenticated request and reject it before the token check even matters.
- **Origin header check:** As a third, independent layer, even in edge cases where SameSite cookie behavior might be bypassed (older browsers, misconfigured proxies), checking that the `Origin` header matches the bank's own domain gives a defense that doesn't rely on cookie attributes at all — it's validating the request's actual network origin.

**Why three layers instead of one:** This is deliberate defense-in-depth — each mechanism closes a different class of bypass. A token alone can theoretically leak via XSS; `SameSite` alone doesn't help legacy browsers; an Origin check alone can be spoofed in certain non-browser contexts. Together, an attacker would need to simultaneously defeat all three, which is a meaningfully higher bar than defeating any single mechanism.

## Result — Attack Confirmed
Balance dropped from R10000 to R1 (R9999 transferred to "attacker") with zero clicks on my part — purely from opening evil_page.html in a separate tab while logged in. The server log confirms it: `TRANSFER LOGGED: lethabo sent R9999 to attacker. New balance: R1`. This happened immediately after opening the attacker page, with no form submission on my end — proving the browser attached my valid session cookie to a request that originated from a completely unrelated, attacker-controlled page, and the server had no way to distinguish that from a legitimate request.