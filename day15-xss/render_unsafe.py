"""Renders a comment into an HTML page fragment by gluing the stored text straight in."""
import sqlite3

def render_comment_unsafe(comment_id: int) -> str:
    conn = sqlite3.connect("comments.db")
    cur = conn.cursor()
    cur.execute("SELECT author, body FROM comments WHERE id = ?", (comment_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return "<p>Comment not found.</p>"
    author, body = row
    # VULNERABLE: author/body are concatenated straight into HTML, unescaped.
    return f"<p><strong>{author}:</strong> {body}</p>"