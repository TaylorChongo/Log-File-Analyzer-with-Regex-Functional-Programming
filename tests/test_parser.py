"""Tests for parse_line in logfile_analyzer.parser."""

from datetime import datetime, timezone

from logfile_analyzer.parser import parse_line


def test_parse_line_returns_dictionary(valid_line):
    entry = parse_line(valid_line)

    assert entry is not None
    assert entry["ip"] == "192.168.1.10"
    assert entry["timestamp"] == datetime(2026, 10, 21, 14, 22, 1, tzinfo=timezone.utc)
    assert entry["method"] == "GET"
    assert entry["url"] == "/index.html"
    assert entry["protocol"] == "HTTP/1.1"
    assert entry["status"] == 200
    assert entry["size"] == 5120
    assert entry["referrer"] == "-"
    assert entry["user_agent"].startswith("Mozilla/5.0")


def test_parse_line_turns_dash_size_into_zero():
    line = '10.0.0.5 - - [20/Oct/2026:08:00:00 +0000] "GET /cart HTTP/1.1" 304 - "-" "curl/8.7.1"'
    entry = parse_line(line)

    assert entry is not None
    assert entry["size"] == 0


def test_parse_line_returns_none_for_malformed_lines(malformed_lines):
    for line in malformed_lines:
        assert parse_line(line) is None


def test_parse_line_on_real_log_file(access_log):
    lines = access_log.read_text(encoding="utf-8").splitlines()
    entries = [parse_line(line) for line in lines]
    parsed = [entry for entry in entries if entry is not None]

    # The sample log has about 1-2% malformed lines on purpose.
    assert len(parsed) > 0.95 * len(lines)
    assert len(parsed) < len(lines)
