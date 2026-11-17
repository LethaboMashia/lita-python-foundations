"""
secure_app.py: D18 HARDENED demo clinic site.

One after_request hook stamps six security headers on EVERY response (pages,
404s, static files). The policy is plain data, so it can be reviewed, tested
and changed in one place.
"""
from flask import Flask

app = Flask(__name__)

# Content-Security-Policy: the browser may only load things from our own origin.
# Deliberately NO 'unsafe-inline': all CSS and JS live in /static, so injected
# inline code has nothing to run as.
CSP_DIRECTIVES = [
    "default-src 'self'",       # fallback: only our own origin
    "script-src 'self'",        # scripts only from our origin, never inline
    "object-src 'none'",        # no plugins
    "base-uri 'self'",          # an injected <base> tag cannot redirect relative URLs
    "form-action 'self'",       # forms may only submit back to us
    "frame-ancestors 'none'",   # nobody may frame this site (clickjacking)
]
CSP = "; ".join(CSP_DIRECTIVES)
assert "'unsafe-inline'" not in CSP, "CSP must never allow unsafe-inline"

SECURITY_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",   # HTTPS only, 1 year
    "X-Content-Type-Options": "nosniff",                                   # do not guess file types
    "X-Frame-Options": "DENY",                                             # legacy framing block
    "Referrer-Policy": "strict-origin-when-cross-origin",                  # share only the origin cross-site
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",      # features off
    "Content-Security-Policy": CSP,
}

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body>
  <main>
    <h1>{title}</h1>
    <p>{body}</p>
    <nav><a href="/">Home</a> | <a href="/about">About</a></nav>
  </main>
</body>
</html>"""


@app.after_request
def add_security_headers(resp):
    """Runs after every route, including errors and static files."""
    for name, value in SECURITY_HEADERS.items():
        resp.headers[name] = value
    return resp


@app.route("/")
def home():
    return PAGE.format(title="Demo Clinic Booking", body="Book an appointment online.")


@app.route("/about")
def about():
    return PAGE.format(title="About", body="A demo site built for the LITA D18 security lab.")


if __name__ == "__main__":
    app.run(port=5001, debug=False)