"""secure_app.py - D19 clinic API, hardened with layered authorisation.

Same routes and seed data as vulnerable_app.py. The difference: every route
now asks "is THIS user allowed to do THIS to THIS resource?" and the answer
comes from policy.py, which denies by default.

Layers
    1  policy.py            can(user, action, resource), deny by default
    2  require_role         role gate on admin routes, one deny() exit
    3  scoped queries       other people's records are invisible (404)
    4  field allowlist       PUT /profile accepts display_name only
    5  log_denied()          audit trail of refusals, no sensitive data

Known gap: routes are only as safe as the decorators on them (see README).
Test data only. Localhost only.
"""
import logging
import os
import sqlite3
from functools import wraps

from flask import Flask, g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from policy import can

DB_PATH = "clinic_secure.db"
ALLOWED_ROLES = {"patient", "doctor", "admin"}
EDITABLE_PROFILE_FIELDS = {"display_name"}      # allowlist: nothing else, ever

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
    fresh from the database on every request, so a demotion takes effect
    immediately (it is never cached at login)."""
    uid = session.get("user_id")
    if uid is None:
        return None
    row = get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    return dict(row) if row else None


# ---- LAYER 5: audit logging of refusals --------------------------------------
audit = logging.getLogger("clinic.audit")
audit.setLevel(logging.INFO)
audit.propagate = False
_handler = logging.FileHandler("denied.log", encoding="utf-8")
_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
audit.addHandler(_handler)


def log_denied(status: int, reason: str) -> None:
    """Record THAT access was refused, never WHAT was in the request.
    Logged: time, status, reason code, method, path (no query string), user id,
    role, client IP. Never logged: passwords, request bodies, record notes,
    session cookies, or the username typed at login."""
    user = current_user()
    audit.info("DENIED status=%s reason=%s method=%s path=%s user_id=%s role=%s ip=%s",
               status, reason, request.method, request.path,
               user["id"] if user else "anon", user["role"] if user else "-",
               request.remote_addr)


# ---- LAYER 2: one refusal path, login gate, role gate ------------------------
MESSAGES = {400: "invalid request", 401: "login required",
            403: "forbidden", 404: "not found"}


def deny(status: int, reason: str):
    """ONE exit for every refusal. The client gets a generic message; the
    specific `reason` goes only to the audit log."""
    log_denied(status, reason)
    return jsonify(error=MESSAGES[status]), status


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return deny(401, "no_session")
        return view(*args, **kwargs)
    return wrapper


def require_role(*roles):
    """Allow only users whose role (read fresh from the DB) is in `roles`.
    Anonymous -> 401. Wrong role -> 403."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return deny(401, "no_session")
            if user["role"] not in roles:
                return deny(403, "role_not_allowed")
            return view(*args, **kwargs)
        return wrapper
    return decorator


# ---- Routes ------------------------------------------------------------------
@app.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    row = get_db().execute("SELECT * FROM users WHERE username=?",
                           (str(body.get("username", "")),)).fetchone()
    if row is None or not check_password_hash(row["password_hash"],
                                              str(body.get("password", ""))):
        log_denied(401, "bad_credentials")
        return jsonify(error="invalid credentials"), 401   # one generic message
    session["user_id"] = row["id"]
    return jsonify(ok=True, username=row["username"])


# ---- LAYER 3: ownership-scoped queries (other people's records -> 404) ------
def fetch_record_for(user: dict, record_id: int) -> dict | None:
    """Return the record ONLY if it belongs to this user (as patient or as
    treating doctor). Anything else is None, so a caller cannot tell 'not
    yours' from 'does not exist'."""
    column = {"patient": "patient_id", "doctor": "doctor_id"}.get(user["role"])
    if column is None:
        return None
    row = get_db().execute(
        f"SELECT * FROM records WHERE id=? AND {column}=?",   # column is a fixed literal
        (record_id, user["id"])).fetchone()
    return dict(row) if row else None


@app.get("/records/<int:record_id>")
@login_required
def get_record(record_id: int):
    user = current_user()
    record = fetch_record_for(user, record_id)
    if record is None:
        return deny(404, "record_not_visible_or_missing")
    if not can(user, "record:read", record):
        return deny(403, "policy_denied_read")
    return jsonify(record)


@app.put("/records/<int:record_id>")
@login_required
def update_record(record_id: int):
    user = current_user()
    record = fetch_record_for(user, record_id)
    if record is None:
        return deny(404, "record_not_visible_or_missing")
    if not can(user, "record:write", record):
        return deny(403, "policy_denied_write")
    notes = (request.get_json(silent=True) or {}).get("notes")
    if not isinstance(notes, str) or len(notes) > 2000:
        return deny(400, "invalid_notes")
    db = get_db()
    db.execute("UPDATE records SET notes=? WHERE id=?", (notes, record_id))
    db.commit()
    return jsonify(ok=True)


@app.get("/admin/users")
@require_role("admin")
def admin_users():
    rows = get_db().execute("SELECT id, username, role FROM users").fetchall()
    return jsonify([dict(r) for r in rows])


@app.put("/admin/users/<int:user_id>")
@require_role("admin")
def admin_set_role(user_id: int):
    role = (request.get_json(silent=True) or {}).get("role", "")
    if role not in ALLOWED_ROLES:
        return deny(400, "invalid_role")
    db = get_db()
    cur = db.execute("UPDATE users SET role=? WHERE id=?", (role, user_id))
    db.commit()
    if cur.rowcount == 0:
        return deny(404, "no_such_user")
    return jsonify(ok=True)


# ---- LAYER 4: field allowlist (kills mass assignment) ------------------------
@app.put("/profile")
@login_required
def update_profile():
    user = current_user()
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not body:
        return deny(400, "empty_or_invalid_body")
    extra = set(body) - EDITABLE_PROFILE_FIELDS
    if extra:
        # Reject the WHOLE request: no partial writes, nothing silently ignored.
        # Truncated so an attacker cannot bloat the log with a huge key name.
        return deny(400, ("disallowed_fields:" + str(sorted(extra)))[:80])
    name = body["display_name"]
    if not isinstance(name, str) or not 1 <= len(name) <= 60:
        return deny(400, "invalid_display_name")
    db = get_db()
    db.execute("UPDATE users SET display_name=? WHERE id=?", (name, user["id"]))
    db.commit()
    return jsonify(ok=True, updated=["display_name"])


if __name__ == "__main__":
    init_db()
    print("Hardened clinic API. Local test data only.")
    app.run(host="127.0.0.1", port=5000, debug=False)