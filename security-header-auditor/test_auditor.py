"""test_auditor.py - unit tests for auditor.py.

No real network calls: requests.get is mocked. Run with:  python -m pytest -v
"""
from unittest.mock import MagicMock, patch

import requests

import auditor

FULL = {name: "x" for name in auditor.CHECKS}      # a fake site that sends all six headers


def test_full_headers_score_100():
    """A site sending every header scores 100 and nothing is missing."""
    score, results = auditor.audit(FULL)
    assert score == 100
    assert all(item["present"] for item in results)


def test_no_headers_score_zero():
    """A site sending none of the headers scores 0."""
    score, results = auditor.audit({})
    assert score == 0
    assert not any(item["present"] for item in results)


def test_header_names_are_case_insensitive():
    """HTTP header names are case-insensitive, so x-frame-options still counts."""
    score, _ = auditor.audit({"x-frame-options": "DENY"})
    assert score == 15


def test_weights_total_100():
    """The six weights must add up to exactly 100 or the score is meaningless."""
    assert sum(weight for weight, _ in auditor.CHECKS.values()) == 100


def test_localhost_allowed():
    """Your own machine is always allowed, with or without a port."""
    assert auditor.is_allowed("http://127.0.0.1:8080", set())
    assert auditor.is_allowed("http://localhost", set())


def test_unknown_host_refused():
    """A host that is not yours and not listed must be refused."""
    assert not auditor.is_allowed("https://example.com", set())


def test_owned_site_allowed():
    """A host you listed as yours is allowed, whatever the path."""
    assert auditor.is_allowed("https://mysite.co.za/page", {"mysite.co.za"})


def test_load_owned_sites_ignores_comments(tmp_path):
    """Comments and blank lines are skipped; names are lower-cased and trimmed."""
    file = tmp_path / "owned.txt"
    file.write_text("# my sites\nmysite.co.za\n\n  Other.CO.za  \n", encoding="utf-8")
    assert auditor.load_owned_sites(file) == {"mysite.co.za", "other.co.za"}


def test_load_owned_sites_missing_file(tmp_path):
    """No owned_sites.txt means no extra sites are allowed, and no crash."""
    assert auditor.load_owned_sites(tmp_path / "nope.txt") == set()


def test_fetch_headers_success():
    """On success we get the headers back and no error."""
    fake = MagicMock()
    fake.headers = {"X-Frame-Options": "DENY"}
    with patch("auditor.requests.get", return_value=fake):
        headers, error = auditor.fetch_headers("http://127.0.0.1")
    assert error is None
    assert headers == {"X-Frame-Options": "DENY"}


def test_fetch_headers_network_error():
    """A network failure becomes an error message, not a crash."""
    with patch("auditor.requests.get", side_effect=requests.ConnectionError("down")):
        headers, error = auditor.fetch_headers("http://127.0.0.1")
    assert headers is None
    assert "down" in error


def test_rating_bands():
    """Scores map to Strong, Fair or Weak."""
    assert auditor.rating(90) == "Strong"
    assert auditor.rating(60) == "Fair"
    assert auditor.rating(40) == "Weak"


def test_report_lists_missing_fix():
    """The report marks missing headers and includes a fixes section."""
    score, results = auditor.audit({})
    text = auditor.build_report("http://127.0.0.1", score, results)
    assert "MISSING" in text
    assert "Recommended fixes" in text



def test_fetch_headers_does_not_follow_redirects():
    """Redirects must not be followed: the gate only vetted the typed URL."""
    fake = MagicMock()
    fake.headers = {}
    with patch("auditor.requests.get", return_value=fake) as mock_get:
        auditor.fetch_headers("http://127.0.0.1")
    mock_get.assert_called_once_with("http://127.0.0.1", timeout=5, allow_redirects=False)
