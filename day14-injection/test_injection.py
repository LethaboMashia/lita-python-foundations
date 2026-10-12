"""test_injection.py - proves the vulnerability and the fix with
automated tests. Run with: pytest -v
"""
import pytest
from setup_db import setup_database
from login_unsafe import login_unsafe
from login_safe import login_safe

ATTACK_PASSWORD = "' OR '1'='1"


@pytest.fixture(autouse=True)
def fresh_database():
    """Re-seed the database before every test, so tests never depend on
    leftover state from a previous test or run."""
    setup_database()


def test_unsafe_login_is_exploitable():
    """login_unsafe must be breakable with the classic payload - this
    test documents the vulnerability exists, so a future fix doesn't
    get silently removed and accidentally reintroduce it."""
    result = login_unsafe("nobody@nowhere.com", ATTACK_PASSWORD)
    assert result is not None  # the attack succeeds - a row comes back


def test_safe_login_resists_injection():
    """login_safe must reject the exact same payload that breaks the
    unsafe version - this is the test that proves the fix works."""
    result = login_safe("nobody@nowhere.com", ATTACK_PASSWORD)
    assert result is None  # parameterised query treats it as a literal


def test_safe_login_still_works_for_real_credentials():
    """A sanity check: the fix shouldn't break legitimate logins."""
    result = login_safe("alice@example.com", "alicepass123")
    assert result is not None
    assert result[1] == "alice@example.com"