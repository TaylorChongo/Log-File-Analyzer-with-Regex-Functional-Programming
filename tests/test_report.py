"""Tests for the report in logfile_analyzer.report."""

from datetime import datetime, timezone

from logfile_analyzer.report import build_report, load_entries, top_n


def make_entry(status, url, ip="10.0.0.5", method="GET"):
    """Make a small fake entry for report tests."""
    return {
        "ip": ip,
        "timestamp": datetime(2026, 10, 20, 9, 30, tzinfo=timezone.utc),
        "method": method,
        "url": url,
        "status": status,
        "size": 100,
    }


def test_top_n():
    counts = {"a": 1, "b": 5, "c": 3}

    assert top_n(counts, 2) == [("b", 5), ("c", 3)]


def test_load_entries_reads_and_parses(sample_log, capsys):
    entries, lines_read = load_entries([sample_log])

    assert lines_read == 8
    assert len(entries) == 5
    assert "processed 8 lines..." in capsys.readouterr().out


def test_build_report():
    entries = [
        make_entry(200, "/products/107?ref=home"),
        make_entry(200, "/products/107"),
        make_entry(404, "/missing", method="POST"),
    ]

    report = build_report(entries, lines_read=4)

    assert "Malformed lines:    1" in report
    assert "Errors (4xx/5xx):   1" in report
    assert "Not found (404):    1" in report
    assert "POST requests:      1" in report
    assert "Total bytes sent:   300" in report
    assert "2  /products/107" in report  # both URLs counted as one page
    assert "09:00  3" in report


def test_build_report_on_real_log_files(access_log):
    entries, lines_read = load_entries([access_log])
    report = build_report(entries, lines_read)

    assert "Lines read:         1500" in report
    assert "Top 5 pages:" in report
