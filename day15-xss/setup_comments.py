"""Creates comments.db with one stored comment, for both render functions to read."""
import sqlite3

def setup():
    conn = sqlite3.connect("comments.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS comments")
    cur.execute("CREATE TABLE comments (id INTEGER PRIMARY KEY, author TEXT, body TEXT)")
    cur.execute(
        "INSERT INTO comments (author, body) VALUES (?, ?)",
        ("alice", "Great clinic, thanks!"),
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup()
    print("comments.db ready with 1 seed comment.")