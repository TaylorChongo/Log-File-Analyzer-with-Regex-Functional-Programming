"""Tests for the regex patterns in logfile_analyzer.patterns."""

from logfile_analyzer.patterns import LOG_PATTERN


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
