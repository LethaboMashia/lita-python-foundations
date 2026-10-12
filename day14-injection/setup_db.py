"""setup_db.py - creates a fresh users table seeded with two accounts.

Run this once before testing login_unsafe or login_safe. It deletes any
existing database file first, so every run starts from a known state.
"""
import sqlite3
import os

DB_FILE = "users.db"


def setup_database():
    """Delete any old database and create a fresh users table with two rows."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)  # start clean every time this runs

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0
        )
    """)

    # Seed two users - a normal one and an admin, so a successful attack
    # has something worth stealing.
    cursor.execute(
        "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
        ("alice@example.com", "alicepass123", 0)
    )
    cursor.execute(
        "INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)",
        ("admin@example.com", "SuperSecret!2026", 1)
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
    print(f"{DB_FILE} created and seeded with 2 users.")