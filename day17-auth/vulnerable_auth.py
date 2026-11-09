"""
vulnerable_auth.py — D17 Auth Lab (INTENTIONALLY INSECURE)

A minimal Flask login system with four routes: /register, /login,
/dashboard, /logout. Every weakness here is deliberate so the three
attacks in attacks.py can be observed working before any fix is applied.
"""

from flask import Flask, request, redirect, make_response

app = Flask(__name__)

# In-memory "database". Plaintext passwords — the first weakness.
users = {}  # username -> password (plaintext)

# Session store: maps a session ID to a username.
# IDs are a simple incrementing integer — the second weakness.
sessions = {}
next_id = 1

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
        users[username] = password  # stored as plaintext
        return redirect("/login")
    return REGISTER_PAGE

@app.route("/login", methods=["GET", "POST"])
def login():
    global next_id
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username not in users:
            return "User not found", 404

        if users[username] != password:
            return "Invalid password", 401

        # Weakness: session ID is just the next integer, and it is
        # assigned fresh here — but nothing stops an old ID from
        # already existing and staying valid too (see logout).
        session_id = next_id
        next_id += 1
        sessions[session_id] = username

        resp = make_response(redirect("/dashboard"))
        resp.set_cookie("session_id", str(session_id))
        return resp
    return LOGIN_PAGE

@app.route("/dashboard")
def dashboard():
    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in sessions:
        return redirect("/login")
    username = sessions[int(session_id)]
    return f"<h2>Welcome, {username}</h2><p>This is your private dashboard.</p><a href='/logout'>Logout</a>"

@app.route("/logout")
def logout():
    # Weakness: this only clears the cookie on the browser.
    # It does NOT delete the entry from `sessions`, so the
    # session ID itself is still valid on the server forever.
    resp = make_response(redirect("/login"))
    resp.delete_cookie("session_id")
    return resp

if __name__ == "__main__":
    app.run(debug=True, port=5000)