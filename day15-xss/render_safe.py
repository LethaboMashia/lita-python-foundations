"""Renders the same comment, escaping untrusted fields before they enter the HTML."""
import sqlite3
import html

def render_comment_safe(comment_id: int) -> str:
    conn = sqlite3.connect("comments.db")
    cur = conn.cursor()
    cur.execute("SELECT author, body FROM comments WHERE id = ?", (comment_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return "<p>Comment not found.</p>"
    author, body = row
    # FIX: escape() converts < > & " ' into their HTML-safe equivalents
    # before they ever reach the markup string. The browser can no longer read
    # anything in author/body as a tag or an attribute, only as printable text.
    safe_author = html.escape(author)
    safe_body = html.escape(body)
    return f"<p><strong>{safe_author}:</strong> {safe_body}</p>"