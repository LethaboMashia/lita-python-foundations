"""demo_attack.py - proves the attack works against login_unsafe and
fails against login_safe, using the identical payload against both.
"""
from setup_db import setup_database
from login_unsafe import login_unsafe
from login_safe import login_safe

ATTACK_PASSWORD = "' OR '1'='1"


def run_demo():
    setup_database()

    print("=== Attacking login_unsafe ===")
    print(f"email='attacker@evil.com', password={ATTACK_PASSWORD!r}")
    result_unsafe = login_unsafe("attacker@evil.com", ATTACK_PASSWORD)
    print("Result:", result_unsafe)
    if result_unsafe:
        print(">>> BROKEN IN - logged in as:", result_unsafe)
    else:
        print(">>> Login failed (unexpected for the unsafe version)")

    print()
    print("=== Same attack against login_safe ===")
    print(f"email='attacker@evil.com', password={ATTACK_PASSWORD!r}")
    result_safe = login_safe("attacker@evil.com", ATTACK_PASSWORD)
    print("Result:", result_safe)
    if result_safe is None:
        print(">>> Correctly rejected. The payload was treated as a literal string.")
    else:
        print(">>> UNEXPECTED - the safe version should never return a row here")


if __name__ == "__main__":
    run_demo()