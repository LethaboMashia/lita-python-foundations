"""login_unsafe.py - login built by string concatenation. VULNERABLE.

Never write real authentication this way. This file exists to prove, with
real output, exactly how SQL injection works against this login function.
"""
import sqlite3

DB_FILE = "users.db"


def login_unsafe(email, pw):
    """Return the matching user row, or None. Built by gluing strings -
    the user's input becomes part of the SQL grammar, not just its data."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # THE VULNERABILITY: email and pw are pasted directly into the query
    # string. The database receives one finished sentence and has no way
    # to tell which parts came from the programmer and which came from
    # whoever typed into the password box.
    query = "SELECT * FROM users WHERE email = '" + email + "' AND password = '" + pw + "'"

    cursor.execute(query)
    row = cursor.fetchone()
    conn.close()
    return row