"""
test_auth.py — D17 Auth Lab
Six pytest tests proving the defences in secure_auth.py work.
Run: python -m pytest day17-auth\test_auth.py -v
"""
import importlib.util
import os

import pytest
from werkzeug.security import check_password_hash

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "secure_auth", os.path.join(HERE, "secure_auth.py")
)
secure_auth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(secure_auth)


@pytest.fixture
def client():
    """Fresh empty app state for every test."""
    secure_auth.users.clear()
    secure_auth.sessions.clear()
    secure_auth.failed_attempts.clear()
    secure_auth.app.config["TESTING"] = True
    with secure_auth.app.test_client() as c:
        yield c


def test_password_is_hashed(client):
    client.post("/register", data={"username": "alice", "password": "mypassword"})
    stored = secure_auth.users["alice"]
    assert stored != "mypassword"
    assert check_password_hash(stored, "mypassword")


def test_same_password_gives_different_hashes(client):
    client.post("/register", data={"username": "bob", "password": "same"})
    client.post("/register", data={"username": "carol", "password": "same"})
    assert secure_auth.users["bob"] != secure_auth.users["carol"]


def test_session_id_is_random_and_new_each_login(client):
    client.post("/register", data={"username": "dave", "password": "pw"})
    r1 = client.post("/login", data={"username": "dave", "password": "pw"})
    r2 = client.post("/login", data={"username": "dave", "password": "pw"})
    t1 = r1.headers["Set-Cookie"].split("session_id=")[1].split(";")[0]
    t2 = r2.headers["Set-Cookie"].split("session_id=")[1].split(";")[0]
    assert len(t1) > 20 and not t1.isdigit()
    assert t1 != t2


def test_wrong_username_and_wrong_password_look_identical(client):
    client.post("/register", data={"username": "eve", "password": "pw"})
    r1 = client.post("/login", data={"username": "nobody", "password": "pw"})
    r2 = client.post("/login", data={"username": "eve", "password": "wrong"})
    assert r1.status_code == r2.status_code == 401
    assert r1.data == r2.data


def test_sixth_failed_attempt_is_locked_out(client):
    client.post("/register", data={"username": "frank", "password": "pw"})
    for _ in range(5):
        r = client.post("/login", data={"username": "frank", "password": "bad"})
        assert r.status_code == 401
    r = client.post("/login", data={"username": "frank", "password": "bad"})
    assert r.status_code == 403
    assert b"locked" in r.data.lower()


def test_logout_invalidates_session_on_server(client):
    client.post("/register", data={"username": "grace", "password": "pw"})
    client.post("/login", data={"username": "grace", "password": "pw"})
    token = list(secure_auth.sessions.keys())[0]
    client.get("/logout")
    assert token not in secure_auth.sessions