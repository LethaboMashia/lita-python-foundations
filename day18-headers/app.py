"""
app.py: D18 BASELINE (no security headers added).
A small demo clinic site with two routes. Audited first, hardened later.
"""
from flask import Flask

app = Flask(__name__)

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


@app.route("/")
def home():
    return PAGE.format(title="Demo Clinic Booking", body="Book an appointment online.")


@app.route("/about")
def about():
    return PAGE.format(title="About", body="A demo site built for the LITA D18 security lab.")


if __name__ == "__main__":
    app.run(port=5000, debug=False)