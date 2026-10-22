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

# --- Validation patterns -------------------------------------------------

# One part of an IP address: a number from 0 to 255.
#   25[0-5]   -> 250-255
#   2[0-4]\d  -> 200-249
#   1?\d?\d   -> 0-199
OCTET = r"(?:25[0-5]|2[0-4]\d|1?\d?\d)"

# Four octets separated by dots: 192.168.1.10
IP_PATTERN = re.compile(OCTET + r"(?:\." + OCTET + r"){3}")

# http:// or https://, a domain name, then an optional path: https://example.com/about
URL_PATTERN = re.compile(r"https?://[\w.-]+(?:/\S*)?")

# name@domain.ext, where the domain has at least one dot: user.name@mail.example.com
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")


def is_valid_ip(text: str) -> bool:
    """Return True if the whole text is a valid IP address, e.g. 192.168.1.10."""
    # fullmatch: the WHOLE text must match, not just the beginning.
    return IP_PATTERN.fullmatch(text) is not None


def is_valid_url(text: str) -> bool:
    """Return True if the whole text is a valid http/https URL."""
    return URL_PATTERN.fullmatch(text) is not None


def is_valid_email(text: str) -> bool:
    """Return True if the whole text is a valid email address."""
    return EMAIL_PATTERN.fullmatch(text) is not None


# --- Searching -----------------------------------------------------------

def find_first_ip(text: str) -> str | None:
    """Return the first IP address found anywhere in the text, or None."""
    match = IP_PATTERN.search(text)
    if match is None:
        return None
    return match.group()


def find_ips(text: str) -> list[str]:
    """Return every IP address found in the text, as a list."""
    return IP_PATTERN.findall(text)


# --- Cleaning with re.sub ------------------------------------------------

def strip_query_string(url: str) -> str:
    """Remove "?" and everything after it: /products/107?ref=home -> /products/107."""
    return re.sub(r"\?.*", "", url)


def mask_ip(ip: str) -> str:
    """Hide the last part of an IP for privacy: 192.168.1.16 -> 192.168.1.xxx."""
    return re.sub(r"\.\d{1,3}$", ".xxx", ip)
