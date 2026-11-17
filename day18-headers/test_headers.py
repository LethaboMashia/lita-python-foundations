"""
test_headers.py: D18. Proves secure_app.py sends the six headers everywhere.
Run: python -m pytest day18-headers\test_headers.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from secure_app import app

SIX = [
    "Strict-Transport-Security",
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Content-Security-Policy",
]
PATHS = ["/", "/about", "/does-not-exist", "/static/style.css"]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.mark.parametrize("path", PATHS)
def test_all_six_headers_on_every_response(client, path):
    r = client.get(path)
    for h in SIX:
        assert h in r.headers, f"{h} missing on {path}"


def test_404_carries_the_headers(client):
    r = client.get("/this-page-does-not-exist")
    assert r.status_code == 404
    assert all(h in r.headers for h in SIX)


def test_simple_header_values(client):
    r = client.get("/")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert r.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_csp_has_required_directives(client):
    csp = client.get("/").headers["Content-Security-Policy"]
    for d in ["default-src", "script-src 'self'", "object-src 'none'",
              "base-uri", "form-action", "frame-ancestors 'none'"]:
        assert d in csp, f"CSP missing {d}"


def test_csp_has_no_unsafe_inline(client):
    csp = client.get("/").headers["Content-Security-Policy"]
    assert "'unsafe-inline'" not in csp


def test_hsts_max_age_is_at_least_one_year(client):
    hsts = client.get("/").headers["Strict-Transport-Security"]
    assert int(hsts.split("max-age=")[1].split(";")[0]) >= 31536000