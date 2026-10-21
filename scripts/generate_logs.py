"""Generate sample Apache/Nginx access logs in Combined Log Format.

Usage:
    python scripts/generate_logs.py                      # default files in data/
    python scripts/generate_logs.py -n 50000 -o data/big.log

Each line looks like:
    192.168.1.10 - - [21/Oct/2026:14:22:01 +0000] "GET /index.html HTTP/1.1" 200 5120 "-" "Mozilla/5.0 ..."

Lines are written in chronological order (useful for takewhile time filtering).
A small share of malformed lines is mixed in so the parser has something to reject.
"""

import argparse
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

IPS = [f"192.168.1.{i}" for i in range(2, 40)] + [
    "10.0.0.5", "10.0.0.17", "172.16.4.21", "203.0.113.7", "198.51.100.23",
    "8.8.8.8", "66.249.66.1", "157.55.39.10",
]
METHODS = ["GET"] * 14 + ["POST"] * 4 + ["PUT", "DELETE", "HEAD", "PATCH"]
PATHS = [
    "/", "/index.html", "/about", "/contact", "/products", "/products/42",
    "/products/107?ref=home", "/cart", "/checkout", "/login", "/logout",
    "/api/v1/users", "/api/v1/users/17", "/api/v1/orders", "/api/v1/orders/993",
    "/search?q=python+regex", "/static/css/main.css", "/static/js/app.js",
    "/images/logo.png", "/favicon.ico", "/robots.txt", "/admin", "/wp-login.php",
]
STATUSES = [200] * 30 + [201, 204, 301, 302, 304, 304] + [400, 401, 403, 404, 404, 404] + [500, 502, 503]
REFERRERS = ["-", "-", "-", "https://www.google.com/", "https://example.com/", "https://news.ycombinator.com/"]
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "curl/8.7.1",
    "python-requests/2.32.3",
]
MALFORMED = [
    "",
    "this is not a log line",
    '999.1.1 - - [bad date] "GET / HTTP/1.1" 200 12',
    '192.168.1.5 - - [21/Oct/2026:10:00:00 +0000] "BROKEN REQUEST" abc -',
]


def make_line(rng: random.Random, when: datetime) -> str:
    status = rng.choice(STATUSES)
    size = "-" if status in (204, 304) else str(rng.randint(150, 60_000))
    return (
        f'{rng.choice(IPS)} - - [{when.strftime("%d/%b/%Y:%H:%M:%S %z")}] '
        f'"{rng.choice(METHODS)} {rng.choice(PATHS)} HTTP/1.1" {status} {size} '
        f'"{rng.choice(REFERRERS)}" "{rng.choice(AGENTS)}"'
    )


def generate(path: Path, count: int, start: datetime, seed: int, malformed_rate: float) -> None:
    rng = random.Random(seed)
    when = start
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for _ in range(count):
            when += timedelta(seconds=rng.randint(1, 90))
            line = rng.choice(MALFORMED) if rng.random() < malformed_rate else make_line(rng, when)
            fh.write(line + "\n")
    print(f"wrote {count} lines to {path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-n", "--lines", type=int, help="number of lines (single-file mode)")
    ap.add_argument("-o", "--output", type=Path, help="output file (single-file mode)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--malformed-rate", type=float, default=0.01)
    args = ap.parse_args()

    start = datetime(2026, 10, 20, 0, 0, 0, tzinfo=timezone.utc)
    if args.output:
        generate(args.output, args.lines or 1000, start, args.seed, args.malformed_rate)
        return

    data = Path(__file__).resolve().parent.parent / "data"
    generate(data / "access.log", 1500, start, args.seed, args.malformed_rate)
    generate(data / "access_2.log", 1000, start + timedelta(days=1), args.seed + 1, args.malformed_rate)


if __name__ == "__main__":
    main()
