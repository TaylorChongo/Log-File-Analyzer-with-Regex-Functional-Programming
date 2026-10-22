"""Tests for the regex patterns in logfile_analyzer.patterns."""

from logfile_analyzer.patterns import (
    LOG_PATTERN,
    find_first_ip,
    find_ips,
    is_valid_email,
    is_valid_ip,
    is_valid_url,
    mask_ip,
    strip_query_string,
)


def test_log_pattern_extracts_named_groups(valid_line):
    match = LOG_PATTERN.match(valid_line)

    assert match is not None
    assert match["ip"] == "192.168.1.10"
    assert match["timestamp"] == "21/Oct/2026:14:22:01 +0000"
    assert match["method"] == "GET"
    assert match["url"] == "/index.html"
    assert match["protocol"] == "HTTP/1.1"
    assert match["status"] == "200"
    assert match["size"] == "5120"
    assert match["referrer"] == "-"
    assert match["user_agent"].startswith("Mozilla/5.0")


def test_log_pattern_accepts_dash_as_size():
    line = '10.0.0.5 - - [20/Oct/2026:08:00:00 +0000] "GET /cart HTTP/1.1" 304 - "-" "curl/8.7.1"'
    match = LOG_PATTERN.match(line)

    assert match is not None
    assert match["size"] == "-"


def test_log_pattern_rejects_malformed_lines(malformed_lines):
    for line in malformed_lines:
        assert LOG_PATTERN.match(line) is None


def test_log_pattern_rejects_non_numeric_status():
    line = '192.168.1.5 - - [21/Oct/2026:10:00:00 +0000] "BROKEN REQUEST" abc -'
    assert LOG_PATTERN.match(line) is None


def test_is_valid_ip():
    assert is_valid_ip("192.168.1.10")
    assert is_valid_ip("0.0.0.0")
    assert is_valid_ip("255.255.255.255")

    assert not is_valid_ip("256.1.1.1")
    assert not is_valid_ip("999.1.1")
    assert not is_valid_ip("192.168.1")
    assert not is_valid_ip("192.168.1.10 extra")
    assert not is_valid_ip("abc")


def test_is_valid_url():
    assert is_valid_url("https://www.google.com/")
    assert is_valid_url("http://example.com")
    assert is_valid_url("https://example.com/products/42?ref=home")

    assert not is_valid_url("-")
    assert not is_valid_url("www.google.com")
    assert not is_valid_url("ftp://example.com")


def test_is_valid_email():
    assert is_valid_email("user@example.com")
    assert is_valid_email("first.last+tag@mail.example.org")

    assert not is_valid_email("user@example")
    assert not is_valid_email("user.example.com")
    assert not is_valid_email("@example.com")


def test_find_first_ip():
    assert find_first_ip("request from 10.0.0.5 then 8.8.8.8") == "10.0.0.5"
    assert find_first_ip("no address here") is None


def test_find_ips():
    assert find_ips("request from 10.0.0.5 then 8.8.8.8") == ["10.0.0.5", "8.8.8.8"]
    assert find_ips("no address here") == []


def test_strip_query_string():
    assert strip_query_string("/products/107?ref=home") == "/products/107"
    assert strip_query_string("/search?q=python+regex") == "/search"
    assert strip_query_string("/about") == "/about"


def test_mask_ip():
    assert mask_ip("192.168.1.16") == "192.168.1.xxx"
    assert mask_ip("8.8.8.8") == "8.8.8.xxx"
