# Security Header Auditor

A command-line tool that checks which HTTP security headers a website
sends, scores it out of 100 and saves a Markdown report.

**Safety:** it only audits localhost or hosts listed in owned_sites.txt
(sites you own or have written permission to test).

## Run it
python -m pip install -r requirements.txt
python demo_server.py                      (terminal 1: a local test site)
python auditor.py http://127.0.0.1:8080    (terminal 2)

## Test it
python -m pytest -v

## What it checks (weights are my own design choice)
Strict-Transport-Security 20 | Content-Security-Policy 25
X-Content-Type-Options 15 | X-Frame-Options 15
Referrer-Policy 10 | Permissions-Policy 15

## Sample output
Auditing http://127.0.0.1:8080
MISSING  Strict-Transport-Security
         Fix: Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' (HTTPS only).
MISSING  Content-Security-Policy
         Fix: Add a Content-Security-Policy that limits where scripts and content may load from.
PRESENT  X-Content-Type-Options
PRESENT  X-Frame-Options
PRESENT  Referrer-Policy
MISSING  Permissions-Policy
         Fix: Add a Permissions-Policy that switches off browser features you do not use.
Score: 40/100 (Weak)
Report saved: reports\report-127.0.0.1-2026-10-11.md

## Limits (honest)
- One request to one URL. It does not follow redirects: the authorisation gate only checks the URL you typed, so following a redirect to another host would bypass it.
- It checks that a header exists, not that its value is strong.
- A first-pass screening, not a penetration test.

## What I learned
- HTTP security headers are instructions in the response (Name: Value) that tell the browser to enforce extra protections while it shows the page.
- requests.get follows redirects by default, which can bypass an authorisation gate. Setting allow_redirects=False keeps the ethics check honest.
- Mocking with unittest.mock.patch lets me test network code without touching the network.
- urlparse splits a URL into parts, and comparing hostnames in lowercase handles case-insensitivity.

Studied from a worked solution, rebuilt from memory on 11 October 2026.