# D17 — Auth Lab: Break It Then Fix It

Built a deliberately vulnerable Flask login app, attacked it three ways, hardened it, and re-ran the same unchanged attacks to prove the fixes work.

## The three attacks

**A — Session guessing.** The vulnerable app issued session IDs 1, 2, 3... Looping over IDs 1-20 opened lethabo's and phuti's dashboards with no password.
Stopped by: `secrets.token_urlsafe(32)` (43 random characters). All 20 guesses missed.

**B — Username enumeration.** The vulnerable app returned `404 User not found` vs `401 Invalid password`, revealing which accounts exist.
Stopped by: one generic `401 Invalid username or password` for both cases. (My script still prints "EXISTS" for any 401, so that label is misleading — the real result is that every response is identical.)

**C — Brute force.** No attempt limit, so a 10-word list cracked `sunshine1` on attempt 7.
Stopped by: lockout after 5 failures in 60 seconds (`403`). In the secure run, the correct password at attempt 7 was also refused.
Note: lockout began at attempt 5 of Attack C because Attack B had already logged one failure for the same user.

## Other defences

| Defence | Stops |
|---|---|
| `generate_password_hash` | Plaintext password storage |
| New token at every login | Session fixation |
| `httponly=True`, `samesite="Lax"` cookie flags | Script-based cookie theft, cross-site requests |
| `del sessions[token]` on logout | Broken logout (old session ID still working) |

## What this lab does not protect against

**Timing side-channel.** `check_password_hash` only runs for real usernames, so real users respond slightly slower. A patient attacker measuring milliseconds could still enumerate. Fix: run a dummy hash check for unknown usernames. Also not covered: HTTPS (`Secure` flag), CSRF tokens, persistent storage, and per-IP rate limiting.

## Files
- `vulnerable_auth.py` — intentionally insecure app
- `attacks.py` — 3 attack scripts, unchanged between runs
- `secure_auth.py` — hardened app
- `test_auth.py` — 6 pytest tests
- `predictions.md` — written and committed before any attack was run