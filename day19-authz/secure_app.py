"""secure_app.py - D19 clinic API, hardened with layered authorisation.

Same routes and seed data as vulnerable_app.py. The difference: every route
now asks "is THIS user allowed to do THIS to THIS resource?" and the answer
comes from policy.py, which denies by default.

Layers: 1 policy.py | 2 require_role | 3 ownership-scoped queries (404 for
other people's records) | 4 field allowlist | 5 denied-access logging.
Test data only. Localhost only.
"""

import os
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = "clinic_secure.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "test-only-not-a-real-secret"   # local demo only

# ---- Seed data (fake, fixed IDs so attacks and tests are repeatable) --------
SEED_USERS = [  # id, username, password, role, display_name
    (1, "thabo", "thabo-pass", "patient", "Thabo"),
    (2, "naledi", "naledi-pass", "patient", "Naledi"),
    (3, "dr_dlamini", "doctor-pass", "doctor", "Dr Dlamini"),
    (4, "sysadmin", "admin-pass", "admin", "Sys Admin"),
]
SEED_RECORDS = [  # id, patient_id, doctor_id, notes
    (1, 1, 3, "TEST DATA: Thabo - routine check-up"),
    (2, 2, 3, "TEST DATA: Naledi - allergy review"),
    (3, 2, 3, "TEST DATA: Naledi - follow-up"),
]


def init_db() -> None:
    """Rebuild the database from scratch so every run starts identical."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, role TEXT NOT NULL, display_name TEXT);
        CREATE TABLE records (
            id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL, notes TEXT);
    """)
    for uid, name, pw, role, disp in SEED_USERS:
        db.execute("INSERT INTO users VALUES (?,?,?,?,?)",
                   (uid, name, generate_password_hash(pw), role, disp))
    db.executemany("INSERT INTO records VALUES (?,?,?,?)", SEED_RECORDS)
    db.commit()
    db.close()


# ---- Database and identity helpers ------------------------------------------
def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def current_user() -> dict | None:
    """Who is logged in? The session stores only user_id; the role is read
    fresh from the database on every request (never cached at login)."""
    uid = session.get("user_id")
    if uid is None:
        return None
    row = get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None


def login_required(view):
    """VULNERABLE BY DESIGN: authentication is the ONLY check on any route."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify(error="login required"), 401
        return view(*args, **kwargs)
    return wrapper


# ---- Routes ------------------------------------------------------------------
@app.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    row = get_db().execute("SELECT * FROM users WHERE username=?",
                           (body.get("username", ""),)).fetchone()
    if row is None or not check_password_hash(row["password_hash"],
                                              body.get("password", "")):
        return jsonify(error="invalid credentials"), 401   # one generic message
    session["user_id"] = row["id"]
    return jsonify(ok=True, username=row["username"])


@app.get("/records/<int:record_id>")
@login_required
def get_record(record_id: int):
    # VULN-A: any logged-in user can read ANY record by changing the number.
    row = get_db().execute("SELECT * FROM records WHERE id=?",
                           (record_id,)).fetchone()
    if row is None:
        return jsonify(error="not found"), 404
    return jsonify(dict(row))


@app.put("/records/<int:record_id>")
@login_required
def update_record(record_id: int):
    # VULN: any logged-in user can overwrite ANY record's notes.
    notes = (request.get_json(silent=True) or {}).get("notes", "")
    db = get_db()
    db.execute("UPDATE records SET notes=? WHERE id=?", (notes, record_id))
    db.commit()
    return jsonify(ok=True)


@app.get("/admin/users")
@login_required
def admin_users():
    # VULN-B: no role check; any logged-in user can list every account.
    rows = get_db().execute("SELECT id, username, role FROM users").fetchall()
    return jsonify([dict(r) for r in rows])


@app.put("/admin/users/<int:user_id>")
@login_required
def admin_set_role(user_id: int):
    # VULN: any logged-in user can change anyone's role.
    role = (request.get_json(silent=True) or {}).get("role", "")
    db = get_db()
    db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit()
    return jsonify(ok=True)


@app.put("/profile")
@login_required
def update_profile():
    # VULN-C: mass assignment. Every real column except id/password_hash is
    # writable, which includes "role". This is an allowlist of the whole
    # schema, not of what a user should be allowed to edit.
    body = request.get_json(silent=True) or {}
    db = get_db()
    columns = {r["name"] for r in db.execute("PRAGMA table_info(users)")}
    columns -= {"id", "password_hash"}
    fields = {k: v for k, v in body.items() if k in columns}   # deciding line
    if not fields:
        return jsonify(error="no valid fields"), 400
    sets = ", ".join(f"{k}=?" for k in fields)   # keys come only from real columns
    db.execute(f"UPDATE users SET {sets} WHERE id=?",
               (*fields.values(), current_user()["id"]))
    db.commit()
    return jsonify(ok=True, updated=list(fields))


if __name__ == "__main__":
    init_db()
    print("Hardened clinic API. Local test data only.")
    app.run(host="127.0.0.1", port=5000, debug=False)