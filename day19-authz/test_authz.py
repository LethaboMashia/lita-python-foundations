"""test_authz.py - D19 access-control test matrix (11 rows + policy tests).

Fixed app:        python -m pytest test_authz.py -v
Vulnerable app:   $env:APP_MODULE="vulnerable_app"; python -m pytest test_authz.py -v

Every row gets a brand-new database, so no row can contaminate another.
Rows that change data also check the DATABASE, not just the status code.
"""
import importlib
import os
import sqlite3

import pytest

APP_MODULE = os.environ.get("APP_MODULE", "secure_app")
PASSWORDS = {"thabo": "thabo-pass", "naledi": "naledi-pass",
             "dr_dlamini": "doctor-pass", "sysadmin": "admin-pass"}


@pytest.fixture
def clinic(tmp_path):
    """A fresh app + database for EVERY test, plus two helpers."""
    mod = importlib.import_module(APP_MODULE)
    mod.DB_PATH = str(tmp_path / "test.db")
    mod.init_db()
    mod.app.config["TESTING"] = True

    def client_for(username=None):
        """A browser-like client. None = anonymous (never logged in)."""
        client = mod.app.test_client()
        if username:
            resp = client.post("/login", json={"username": username,
                                               "password": PASSWORDS[username]})
            assert resp.status_code == 200, f"setup failed: login as {username}"
        return client

    def db_value(sql, params=()):
        """Ask the database directly: the truth, not the server's reply."""
        con = sqlite3.connect(mod.DB_PATH)
        try:
            return con.execute(sql, params).fetchone()[0]
        finally:
            con.close()

    return client_for, db_value


# (row, who, method, path, body, expected status, what it proves, setup steps)
MATRIX = [
    (1, "thabo", "GET", "/records/1", None, 200, "patient reads own record", []),
    (2, "thabo", "GET", "/records/2", None, 404, "cross-user read is invisible", []),
    (3, None, "GET", "/records/1", None, 401, "anonymous cannot read records", []),
    (4, None, "GET", "/admin/users", None, 401, "anonymous cannot reach admin", []),
    (5, "thabo", "GET", "/admin/users", None, 403, "patient cannot reach admin", []),
    (6, "sysadmin", "GET", "/admin/users", None, 200, "admin reaches admin", []),
    (7, "thabo", "PUT", "/profile", {"role": "admin"}, 400, "mass assignment rejected", []),
    (8, "thabo", "PUT", "/profile", {"display_name": "T"}, 200, "legitimate profile write", []),
    (9, "thabo", "PUT", "/records/1", {"notes": "tampered"}, 403, "patient cannot write records", []),
    (10, "dr_dlamini", "PUT", "/records/1", {"notes": "reviewed"}, 200, "doctor writes own patient's record", []),
    (11, "dr_dlamini", "GET", "/records/1", None, 404, "demoted doctor loses access at once",
     [("sysadmin", "PUT", "/admin/users/3", {"role": "patient"})]),
]

# Independent proof from the database for rows that change state.
EFFECTS = {
    7: ("thabo's role is still 'patient'",
        lambda v: v("SELECT role FROM users WHERE id=1") == "patient"),
    8: ("thabo's display_name became 'T'",
        lambda v: v("SELECT display_name FROM users WHERE id=1") == "T"),
    9: ("record 1 notes are unchanged",
        lambda v: v("SELECT notes FROM records WHERE id=1") == "TEST DATA: Thabo - routine check-up"),
    10: ("record 1 notes became 'reviewed'",
         lambda v: v("SELECT notes FROM records WHERE id=1") == "reviewed"),
}


@pytest.mark.parametrize(
    "row,who,method,path,body,expected,why,setup", MATRIX,
    ids=[f"row{m[0]:02d}-{m[6].replace(' ', '_')}" for m in MATRIX])
def test_access_matrix(clinic, row, who, method, path, body, expected, why, setup):
    client_for, db_value = clinic
    client = client_for(who)            # logs in FIRST, so row 11 tests a live session
    for s_who, s_method, s_path, s_body in setup:
        resp = client_for(s_who).open(s_path, method=s_method, json=s_body)
        assert resp.status_code == 200, f"setup step failed: {s_method} {s_path}"
    resp = client.open(path, method=method, json=body)
    assert resp.status_code == expected, \
        f"row {row} ({why}): got {resp.status_code}, expected {expected}"
    if row in EFFECTS:
        description, check = EFFECTS[row]
        assert check(db_value), f"row {row}: database check failed: {description}"


def test_policy_denies_anonymous_and_unknown_roles():
    from policy import can
    assert not can(None, "record:read", {"patient_id": 1})
    nurse = {"id": 9, "role": "nurse"}          # a role the policy never mentions
    for action in ("record:read", "record:write", "user:list",
                   "user:set_role", "profile:update"):
        assert not can(nurse, action, {"patient_id": 9, "doctor_id": 9})


def test_policy_denies_unknown_actions():
    from policy import can
    assert not can({"id": 4, "role": "admin"}, "database:drop")