"""Compiled regex patterns for log formats and validation (IP, URL, email)."""

import re

# One line of an Apache/Nginx access log (Combined Log Format), for example:
# 192.168.1.10 - - [21/Oct/2026:14:22:01 +0000] "GET /index.html HTTP/1.1" 200 5120 "-" "Mozilla/5.0"
#
# Each (?P<name>...) is a named group: the text it matches can later be read
# by name, e.g. match["ip"] or match["status"].
LOG_PATTERN = re.compile(
    r"(?P<ip>\d{1,3}(?:\.\d{1,3}){3}) "                      # 192.168.1.10
    r"\S+ \S+ "                                              # ident and user, usually "- -"
    r"\[(?P<timestamp>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\] "  # [21/Oct/2026:14:22:01 +0000]
    r'"(?P<method>[A-Z]+) (?P<url>\S+) (?P<protocol>[^"]+)" '  # "GET /index.html HTTP/1.1"
    r"(?P<status>\d{3}) "                                    # 200
    r"(?P<size>\d+|-) "                                      # 5120, or "-" when no body was sent
    r'"(?P<referrer>[^"]*)" '                                # "-" or "https://www.google.com/"
    r'"(?P<user_agent>[^"]*)"'                               # "Mozilla/5.0 ..."
)
