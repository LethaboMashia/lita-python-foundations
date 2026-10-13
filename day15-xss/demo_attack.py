"""Posts one attacker comment, then renders it through both functions side by side."""
import sqlite3
from setup_comments import setup
from render_unsafe import render_comment_unsafe
from render_safe import render_comment_safe

ATTACK_BODY = '<img src=x onerror="document.title=\'XSS\'">'

def post_attacker_comment() -> int:
    conn = sqlite3.connect("comments.db")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO comments (author, body) VALUES (?, ?)",
        ("mallory", ATTACK_BODY),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

if __name__ == "__main__":
    setup()
    attacker_id = post_attacker_comment()

    print("--- render_comment_unsafe ---")
    print(render_comment_unsafe(attacker_id))
    print()
    print("--- render_comment_safe ---")
    print(render_comment_safe(attacker_id))