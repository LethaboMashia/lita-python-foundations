# D19: Authorization and Access Control (Break It, Fix It, Prove It)

A small Flask + SQLite clinic API (test data only, localhost only) that I attacked
three ways, fixed in layers, and then proved fixed with an identical attack script
and an 11-row test matrix.

> Authentication asks "who are you?". Authorisation asks "are you allowed to do
> THIS to THIS?". The vulnerable app only ever asked the first question.

## Result

| | Vulnerable app | Fixed app |
|---|---|---|
| A. patient reads another patient's record (`GET /records/2`) | 200, record leaked | 404 |
| B. patient opens `/admin/users` | 200, all accounts listed | 403 |
| C. patient sends `PUT /profile {"role":"admin"}` | 200, role became `admin` | 400, role unchanged |
| `attack.py` (identical script both times) | 3/3 succeeded | 0/3 succeeded |
| Test matrix (13 tests) | 5 failed, 8 passed | 13 passed |

Evidence is committed: `attack_before.txt`, `attack_after.txt`, `matrix_before.txt`,
`matrix_after.txt`, `denied_log_sample.txt`.

## The policy

Four seeded users (patients thabo and naledi, doctor dr_dlamini, admin sysadmin), and
records that carry a `patient_id` and a `doctor_id`.

| Action | Route | patient | doctor | admin | Extra condition |
|---|---|---|---|---|---|
| `record:read` | `GET /records/<id>` | yes | yes | no | must be YOUR record (as patient or treating doctor) |
| `record:write` | `PUT /records/<id>` | no | yes | no | must be your patient's record |
| `user:list` | `GET /admin/users` | no | no | yes | |
| `user:set_role` | `PUT /admin/users/<id>` | no | no | yes | role must be one of three known values |
| `profile:update` | `PUT /profile` | yes | yes | yes | `display_name` only |

Anything not in this table is denied. Admins deliberately have no access to clinical
records: managing accounts is not the same as reading medical notes.

## What each fix stops

| Layer | What it adds | What it stops | Proved by |
|---|---|---|---|
| 1. `policy.py` | `can(user, action, resource)`, deny by default | unknown roles, unknown actions, anonymous users getting anything by accident | policy tests, row 5 |
| 2. `require_role` | role gate plus one `deny()` exit | a patient reaching admin routes (Attack B) | rows 4, 5, 6 |
| 3. Ownership-scoped queries | the SQL only returns rows tied to the caller | reading someone else's record (Attack A) | rows 2, 11 |
| 4. Field allowlist | `PUT /profile` accepts `display_name` and nothing else | mass assignment (Attack C) | row 7 |
| 5. `log_denied()` | audit trail of every refusal | refusals vanishing without a trace | `denied_log_sample.txt` |

## Design decisions

- **404, not 403, for other people's records.** A 403 confirms the record exists. The
  lookup is scoped to the caller, so "not yours" and "does not exist" look identical.
- **Unexpected fields reject the whole request** (400) instead of being silently
  dropped. A request that tries to set `role` is an attack signal worth logging, and
  there are no partial writes.
- **The role is read from the database on every request**, never cached in the
  session. Row 11 proves it: a doctor who is demoted loses access on their very next
  request, even with a session opened before the demotion.
- **Tests check the database, not just the status code.** Status codes are the
  server's report. Rows that change data ask the database directly.
- **One refusal path.** Every refusal goes through `deny()`: generic message to the
  client, specific reason code to the log.
- **Fresh database per test.** Rows 7, 9 and 11 change state, so sharing a database
  would let them corrupt each other.

## What gets logged (and what never does)

Logged: time, status, reason code, method, path (no query string), user id, role,
client IP. Never logged: passwords, request bodies, record notes, session cookies, or
the username typed at login. The reason for a rejected field is truncated so an
attacker cannot bloat the log with a huge key name.

Format: `<time> DENIED status=404 reason=record_not_visible_or_missing method=GET path=/records/2 user_id=1 role=patient ip=127.0.0.1`

## Predictions vs reality

Written and committed before any code existed (`predictions.md`).

- **Right:** the three attacks' "before" codes (200, 200, 200), the "after" codes
  (404, 403, 400), and the matrix count exactly: 5 failures (rows 2, 5, 7, 9, 11) on
  the vulnerable app and 0 on the fixed one.
- **Wrong:** I predicted `/login` would return 200 on my first smoke test. It returned
  401 because PowerShell mangled the escaped quotes in my JSON, the server received an
  empty body, and the login failed. The app was fine; the shell was the problem. I
  moved the JSON to a file, and the attack script uses Python's `requests`, which
  avoids it entirely.
- **Honest note:** my "unsure" items in `predictions.md` flagged the same two things
  that mattered later: whether the role is re-read per request (row 11), and whether
  patients may ever write (row 9).

## What this does not cover

- **No global route guard.** Deny-by-default here applies to decisions that go through
  `can()`. A new route someone forgets to decorate would be open, even to anonymous
  users. A `before_request` guard plus a test that walks `app.url_map` would close it.
- **Login hardening:** no lockout or rate limiting, no MFA, no password reset. (The
  D17 lab covers lockout and session handling.)
- **Transport and cookie settings:** runs over plain HTTP on localhost; no `Secure`,
  `HttpOnly` or `SameSite` cookie configuration; the secret key is hard-coded for the
  demo. The D18 lab covers security headers.
- **No CSRF protection** on state-changing requests.
- **Successful admin actions are not audited.** Only refusals are logged, so a role
  change by an admin leaves no trace.
- **Logs are plain local files:** not tamper-proof, not rotated, not shipped anywhere.
- **Function-level checks only:** no field-level read controls, no per-record sharing,
  no emergency-access ("break glass") path a real clinic would need.
- **Tests use Flask's test client**, not a real network, and this is a teaching
  project, not a penetration test.

## Run it

```powershell
# Vulnerable app, then the attack, then the matrix
python vulnerable_app.py
python attack.py
$env:APP_MODULE = "vulnerable_app"; python -m pytest test_authz.py -v

# Fixed app, the IDENTICAL attack, then the matrix
python secure_app.py
python attack.py
Remove-Item Env:APP_MODULE; python -m pytest test_authz.py -v
```

## Files

`predictions.md` · `vulnerable_app.py` · `attack.py` · `attack_before.txt` ·
`policy.py` · `secure_app.py` · `attack_after.txt` · `test_authz.py` ·
`matrix_before.txt` · `matrix_after.txt` · `denied_log_sample.txt`