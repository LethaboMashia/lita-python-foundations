"""demo_server.py - a tiny local website that sends only THREE of the six security headers.

It lets you test the auditor on your own machine, with a known, repeatable answer.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8080


class Handler(BaseHTTPRequestHandler):
    """Answers every GET request with a short message plus three security headers."""

    def do_GET(self):  # pylint: disable=invalid-name  # the server library requires this exact name
        """Called by the server for each GET request."""
        self.send_response(200)                       # status line: 200 OK
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")    # header 1 of 3 we send
        self.send_header("X-Frame-Options", "DENY")              # header 2 of 3
        self.send_header("Referrer-Policy", "no-referrer")       # header 3 of 3
        self.end_headers()                             # blank line: headers finished, body next
        self.wfile.write(b"LITA demo site\n")          # the body, as bytes


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)  # 127.0.0.1 = this machine only
    print(f"Demo site on http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    server.serve_forever()                             # run until you press Ctrl+C
