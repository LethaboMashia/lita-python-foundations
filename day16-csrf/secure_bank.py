"""
secure_bank.py — Day 16 CSRF Lab (FIXED VERSION)

Same banking app as vulnerable_bank.py, but /transfer is now protected by
three independent, layered defenses. Each one closes a different class of
bypass, so an attacker would need to defeat all three simultaneously:

  1. CSRF token  — a per-session secret embedded in the form, unknown to
                   any page other than the bank's own authenticated dashboard
  2. SameSite=Lax cookie — tells the browser itself not to attach this
                   cookie on cross-site POST requests
  3. Origin header check — validates that the request's actual network
                   origin matches this server's own domain
"""

import secrets
from flask import Flask, request, session, redirect, render_template_string, abort

app = Flask(__name__)
app.secret_key = "insecure-dev-key"  # same note as before: use env vars in real apps

# DEFENSE 2: SameSite=Lax means the browser will NOT attach this cookie
# when a request originates from a different site (which is exactly what
# evil_page.html is, from the browser's point of view). Lax still allows
# the cookie on normal top-level navigation (e.g. clicking a link to the
# site), which is why Lax rather than the stricter Strict is the common
# practical default for apps like this.
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # would be True in production (HTTPS only)
)

balance = {"lethabo": 10000}

LOGIN_PAGE = """
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
"""

# DEFENSE 1 (part 1): the CSRF token is rendered directly into the form as
# a hidden field. An attacker's page has no way to read this value, since
# it can only see the bank's HTML by actually being logged in themselves.
DASHBOARD_PAGE = """
<h2>Welcome, {{ user }}</h2>
<p>Balance: R{{ balance }}</p>
<form method="POST" action="/transfer">
  <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
  Transfer to: <input name="recipient"><br>
  Amount: <input name="amount"><br>
  <button type="submit">Transfer</button>
</form>
<a href="/logout">Logout</a>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "lethabo" and request.form.get("password") == "test123":
            session["user"] = "lethabo"
            # DEFENSE 1 (part 2): generate a fresh, unguessable token at
            # login time and store it server-side in the session. This is
            # the value that will be compared against whatever the form
            # submits on /transfer.
            session["csrf_token"] = secrets.token_hex(32)
            return redirect("/dashboard")
        return "Invalid credentials", 401
    return LOGIN_PAGE

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    user = session["user"]
    return render_template_string(
        DASHBOARD_PAGE,
        user=user,
        balance=balance[user],
        csrf_token=session.get("csrf_token", ""),
    )

@app.route("/transfer", methods=["POST"])
def transfer():
    if "user" not in session:
        return "Not logged in", 401

    # DEFENSE 3: check that the request's Origin header matches this
    # server's own origin. A cross-site request (like one triggered by
    # evil_page.html) will either have no Origin header matching ours,
    # or none at all in some cases — either way, reject it.
    origin = request.headers.get("Origin", "")
    if origin and not origin.startswith("http://127.0.0.1:5000"):
        abort(403)

    # DEFENSE 1 (part 3): compare the token submitted in the form against
    # the one stored server-side in the session. An attacker's forged
    # form has no way to know this value, so it will be missing or wrong.
    submitted_token = request.form.get("csrf_token", "")
    real_token = session.get("csrf_token", "")
    if not submitted_token or submitted_token != real_token:
        abort(403)

    user = session["user"]
    amount = int(request.form.get("amount", 0))
    recipient = request.form.get("recipient", "unknown")
    balance[user] -= amount
    print(f"TRANSFER LOGGED: {user} sent R{amount} to {recipient}. New balance: R{balance[user]}")
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True, port=5000)