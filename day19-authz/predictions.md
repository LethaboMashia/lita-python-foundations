# D19 Predictions: Authorization and Access Control
Written before any code exists. Local test data only.

## Seed data (fixed)
| id | username | role |
|---|---|---|
| 1 | thabo | patient |
| 2 | naledi | patient |
| 3 | dr_dlamini | doctor |
| 4 | sysadmin | admin |

| record id | patient_id | doctor_id |
|---|---|---|
| 1 | 1 (thabo) | 3 |
| 2 | 2 (naledi) | 3 |
| 3 | 2 (naledi) | 3 |

## Access rule assumed
- Patient: reads their own records only, never writes.
- Doctor: reads and writes records where doctor_id is theirs.
- Admin: manages users, no clinical record access.

## The three attacks (logged in as thabo)
| Attack | Status BEFORE fix | Status AFTER fix | Why |
|---|---|---|---|
| A. GET /records/2 | 200 (leaks Naledi's record) | 404 | Before: only authentication was checked, not ownership (IDOR); after: server checks patient_id matches the caller and returns 404 instead of 403 so existence isn't confirmed. |
| B. GET /admin/users | 200 (thabo gets in) | 403 | Before: no role check existed past "are you logged in"; after: endpoint requires role=admin. |
| C. PUT /profile {"role":"admin"} | 200, role becomes admin | 400, role unchanged | Before: mass assignment, any field in the body gets written; after: role is excluded from the user-editable whitelist. |

## Matrix prediction
Before the fix, 5 of the 11 matrix rows will FAIL (rows 2, 5, 7, 9, 11).
After the fix, 0 will fail.
Reasoning for the 5: each of those rows requires a check beyond "is there a valid session": ownership (2, 11), role (5), field whitelisting (7), and write-permission-by-role (9). None of those exist before the fix, so each one succeeds when it should be blocked.

## Unsure about
1. Row 11 assumes authorization is re-evaluated on every request rather than cached at login — if the pre-fix app stashes role in a session/JWT issued before the demotion, dr_dlamini might still get 200 even briefly after the fix is deployed, depending on token lifetime.
2. Row 9 implies patients can never write to their own record (only doctors can) — worth confirming that's the real intended rule and not just "non-owners can't write," since those predict different pre-fix failure counts if patients were meant to have any self-write path.