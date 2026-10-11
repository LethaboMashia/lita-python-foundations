"""auditor.py - Security Header Auditor.

What it does: asks a website for its HTTP response headers, checks which of six
security headers are present, scores the site out of 100 and saves a Markdown report.
Safety rule: it ONLY audits localhost or sites listed in owned_sites.txt.
"""

import sys                                  # sys.argv (what you typed) and sys.exit (exit code)
from datetime import date                    # today's date for the report name
from pathlib import Path                     # modern, cross-platform file paths
from urllib.parse import urlparse            # splits a URL into scheme, host, path, ...

import requests                              # third-party library for making HTTP requests

LOCAL_HOSTS = {"localhost", "127.0.0.1"}     # your own machine: always allowed
OWNED_FILE = Path("owned_sites.txt")         # sites you own or have WRITTEN permission to test

# header name -> (points if present, one-line fix if missing). The points add up to 100.
CHECKS = {
    "Strict-Transport-Security": (
        20, "Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' (HTTPS only)."),
    "Content-Security-Policy": (
        25, "Add a Content-Security-Policy that limits where scripts and content may load from."),
    "X-Content-Type-Options": (
        15, "Add 'X-Content-Type-Options: nosniff'."),
    "X-Frame-Options": (
        15, "Add 'X-Frame-Options: DENY' (or SAMEORIGIN) so other sites cannot frame yours."),
    "Referrer-Policy": (
        10, "Add 'Referrer-Policy: strict-origin-when-cross-origin' (or no-referrer)."),
    "Permissions-Policy": (
        15, "Add a Permissions-Policy that switches off browser features you do not use."),
}


def load_owned_sites(path=OWNED_FILE):
    """Read the allowed hostnames from a text file (one per line, # starts a comment)."""
    if not path.exists():                    # no file yet means no extra sites are allowed
        return set()
    sites = set()                            # a set: fast lookup, no duplicates
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()          # remove spaces, make lowercase so matching is fair
        if line and not line.startswith("#"):    # skip blank lines and comment lines
            sites.add(line)
    return sites


def is_allowed(url, owned_sites):
    """The ethics gate: True only for localhost or a host you have listed as yours."""
    host = (urlparse(url).hostname or "").lower()   # 'https://Site.co.za:8080/x' -> 'site.co.za'
    return host in LOCAL_HOSTS or host in owned_sites


def fetch_headers(url):
    """Return (headers, error). Exactly one of the two is None.

    allow_redirects=False: the ethics gate only checked this exact URL. If the
    site redirected us somewhere else, following it would mean fetching headers
    from a host we never authorised. Refusing to follow keeps the gate honest.
    """
    try:
        response = requests.get(url, timeout=5, allow_redirects=False)
    except requests.RequestException as exc:        # base class for all requests errors
        return None, str(exc)                       # report the problem instead of crashing
    return response.headers, None


def audit(headers):
    """Compare the headers against CHECKS. Return (score, results)."""
    # Header names are case-insensitive on the web, so compare in lowercase.
    lowered = {name.lower(): value for name, value in headers.items()}
    score = 0
    results = []
    for name, (weight, fix) in CHECKS.items():
        present = name.lower() in lowered
        if present:
            score += weight                          # only present headers earn points
        results.append({"header": name, "present": present, "weight": weight, "fix": fix})
    return score, results


def rating(score):
    """Turn the number into a plain word a client understands."""
    if score >= 80:
        return "Strong"
    if score >= 50:
        return "Fair"
    return "Weak"


def build_report(url, score, results):
    """Build the Markdown report text. No printing or saving here: one job only."""
    lines = [
        "# Security Header Report",
        "",
        f"- **Site:** {url}",
        f"- **Date:** {date.today().isoformat()}",
        f"- **Score:** {score}/100 ({rating(score)})",
        "",
        "| Header | Status | Points |",
        "|---|---|---|",
    ]
    for item in results:
        status = "PRESENT" if item["present"] else "MISSING"
        points = item["weight"] if item["present"] else 0
        lines.append(f"| {item['header']} | {status} | {points}/{item['weight']} |")
    missing = [item for item in results if not item["present"]]
    if missing:                                      # fixes section only if there is work to do
        lines += ["", "## Recommended fixes", ""]
        for item in missing:
            lines.append(f"- **{item['header']}:** {item['fix']}")
    return "\n".join(lines) + "\n"


def save_report(url, text):
    """Write the report into a reports/ folder and return its path."""
    host = urlparse(url).hostname or "site"
    folder = Path("reports")
    folder.mkdir(exist_ok=True)                      # create the folder only if it is missing
    path = folder / f"report-{host}-{date.today().isoformat()}.md"
    path.write_text(text, encoding="utf-8")
    return path


def main(argv):
    """Run the tool. Returns an exit code: 0 = ok, non-zero = something went wrong."""
    if len(argv) != 2:                               # argv[0] = script name, argv[1] = the URL
        print("Usage: python auditor.py <url>")
        return 1
    url = argv[1]
    if not is_allowed(url, load_owned_sites()):      # the ethics gate runs BEFORE any request
        print("Refused: that host is not localhost and not listed in owned_sites.txt.")
        print("Only audit sites you own or have written permission to test.")
        return 2
    headers, error = fetch_headers(url)
    if error:
        print(f"Could not reach {url}: {error}")
        return 3
    score, results = audit(headers)
    print(f"Auditing {url}")
    for item in results:
        status = "PRESENT" if item["present"] else "MISSING"
        print(f"{status:<8} {item['header']}")
        if not item["present"]:
            print(f"         Fix: {item['fix']}")
    print(f"Score: {score}/100 ({rating(score)})")
    print(f"Report saved: {save_report(url, build_report(url, score, results))}")
    return 0


if __name__ == "__main__":                           # only when run directly, not on import
    sys.exit(main(sys.argv))
