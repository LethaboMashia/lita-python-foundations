"""login_safe.py - login built with parameterised queries. SAFE.

The SQL grammar is locked (sent to SQLite and parsed) before the user's
data ever arrives. Data can never become command, no matter what it
contains.
"""
import sqlite3

DB_FILE = "users.db"


def login_safe(email, pw):
    """Return the matching user row, or None. Built with ? placeholders -
    email and pw are bound as DATA, after the grammar is already fixed."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # THE FIX: the query string has NO user input in it at all - just two
    # ? placeholders. SQLite parses and locks this grammar first. Only
    # then does execute() deliver (email, pw) as a separate tuple of
    # values, bound into the two slots. Nothing in those values can add
    # a new OR, close a string, or change the grammar - it's just data.
    query = "SELECT * FROM users WHERE email = ? AND password = ?"

    cursor.execute(query, (email, pw))
    row = cursor.fetchone()
    conn.close()
    return row