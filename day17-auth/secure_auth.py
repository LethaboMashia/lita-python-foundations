"""
secure_auth.py — D17 Auth Lab (HARDENED VERSION)
Six defences applied to the vulnerable app.
"""
from flask import Flask, request, redirect, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import time

app = Flask(__name__)

users = {}            # username -> password_hash
sessions = {}          # token (str) -> username
failed_attempts = {}   # username -> [timestamp, timestamp, ...]

LOCKOUT_LIMIT = 5
LOCKOUT_WINDOW = 60  # seconds

LOGIN_PAGE = """
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
"""

REGISTER_PAGE = """
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Register</button>
</form>
"""


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users:
            return "Username already taken", 400
        users[username] = generate_password_hash(password)
        return redirect("/login")
    return REGISTER_PAGE


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        now = time.time()
        attempts = failed_attempts.get(username, [])
        attempts = [t for t in attempts if now - t < LOCKOUT_WINDOW]
        failed_attempts[username] = attempts

        if len(attempts) >= LOCKOUT_LIMIT:
            return "Account temporarily locked. Try again later.", 403

        if username not in users or not check_password_hash(users[username], password):
            failed_attempts.setdefault(username, []).append(now)
            return "Invalid username or password", 401

        failed_attempts.pop(username, None)

        token = secrets.token_urlsafe(32)
        sessions[token] = username

        resp = make_response(redirect("/dashboard"))
        resp.set_cookie("session_id", token, httponly=True, samesite="Lax")
        return resp

    return LOGIN_PAGE


@app.route("/dashboard")
def dashboard():
    token = request.cookies.get("session_id")
    if token is None or token not in sessions:
        return redirect("/login")
    username = sessions[token]
    return f"<h2>Welcome, {username}</h2><p>This is your private dashboard.</p><a href='/logout'>Logout</a>"


@app.route("/logout")
def logout():
    token = request.cookies.get("session_id")
    if token and token in sessions:
        del sessions[token]
    resp = make_response(redirect("/login"))
    resp.delete_cookie("session_id")
    return resp


if __name__ == "__main__":
    app.run(debug=True, port=5000)