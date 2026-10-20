"""
vulnerable_bank.py — Day 16 CSRF Lab (INTENTIONALLY INSECURE)

This is a minimal Flask banking app used to demonstrate Cross-Site Request
Forgery. The /transfer endpoint below is deliberately missing every standard
CSRF defense so the attack in evil_page.html can be observed working end to
end before any fix is applied.
"""

from flask import Flask, request, session, redirect, render_template_string

app = Flask(__name__)
# NOTE: a real app would load this from an environment variable / secrets
# manager, never hardcode it. Kept simple here since secret_key rotation
# isn't the focus of this lab.
app.secret_key = "insecure-dev-key"

# In-memory "database" — resets every time the server restarts.
balance = {"lethabo": 10000}

LOGIN_PAGE = """
<form method="POST">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <button type="submit">Login</button>
</form>
"""

DASHBOARD_PAGE = """
<h2>Welcome, {{ user }}</h2>
<p>Balance: R{{ balance }}</p>
<form method="POST" action="/transfer">
  Transfer to: <input name="recipient"><br>
  Amount: <input name="amount"><br>
  <button type="submit">Transfer</button>
</form>
<a href="/logout">Logout</a>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Hardcoded credential check — fine for a lab, never for production.
        if request.form.get("username") == "lethabo" and request.form.get("password") == "test123":
            session["user"] = "lethabo"
            return redirect("/dashboard")
        return "Invalid credentials", 401
    return LOGIN_PAGE

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    user = session["user"]
    return render_template_string(DASHBOARD_PAGE, user=user, balance=balance[user])

@app.route("/transfer", methods=["POST"])
def transfer():
    """
    THE VULNERABILITY LIVES HERE.

    This route only checks that a valid session exists — it never verifies
    WHERE the request actually came from. A session cookie is attached by
    the browser automatically to any request sent to this server's origin,
    regardless of which page triggered that request. That means a form
    hosted on a completely different domain (evil_page.html) can submit
    a POST here, the browser will attach my real session cookie to it,
    and this code has no way to tell the difference between:

        (a) me clicking "Transfer" on my own dashboard, and
        (b) my browser being silently tricked into submitting a
            forged form from an attacker's page.

    There is no CSRF token to validate, no Origin/Referer header check,
    and the session cookie carries no SameSite restriction — all three
    of the standard defenses are absent by design for this lab.
    """
    if "user" not in session:
        return "Not logged in", 401
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