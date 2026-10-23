"""Tests for the functional pipeline in logfile_analyzer.pipeline."""

from logfile_analyzer.pipeline import (
    count_by,
    has_method,
    has_status,
    is_error,
    is_not_found,
    is_post,
    parse_entries,
    total_bytes,
)
from logfile_analyzer.readers import read_lines

GET_OK = {"method": "GET", "status": 200}
GET_NOT_FOUND = {"method": "GET", "status": 404}
POST_SERVER_ERROR = {"method": "POST", "status": 500}
ENTRIES = [GET_OK, GET_NOT_FOUND, POST_SERVER_ERROR]


def test_parse_entries_skips_malformed_lines(sample_log):
    entries = list(parse_entries(read_lines(sample_log)))

    assert len(entries) == 5  # the 3 malformed lines are dropped
    assert entries[0]["ip"] == "192.168.1.10"


def test_parse_entries_is_lazy(sample_log):
    entries = parse_entries(read_lines(sample_log))

    assert not isinstance(entries, list)
    assert next(entries)["status"] == 200


def test_has_status_and_has_method():
    assert has_status(404, GET_NOT_FOUND)
    assert not has_status(404, GET_OK)
    assert has_method("POST", POST_SERVER_ERROR)
    assert not has_method("POST", GET_OK)


def test_is_error():
    assert list(filter(is_error, ENTRIES)) == [GET_NOT_FOUND, POST_SERVER_ERROR]


def test_partial_filters():
    assert list(filter(is_not_found, ENTRIES)) == [GET_NOT_FOUND]
    assert list(filter(is_post, ENTRIES)) == [POST_SERVER_ERROR]


def test_chained_pipeline(access_log):
    # read -> parse -> keep only 404s, all lazily, one line at a time
    not_found = filter(is_not_found, parse_entries(read_lines(access_log)))

    statuses = [entry["status"] for entry in not_found]
    assert len(statuses) > 0
    assert set(statuses) == {404}


def test_total_bytes():
    entries = [{"size": 100}, {"size": 250}, {"size": 0}]

    assert total_bytes(entries) == 350
    assert total_bytes([]) == 0


def test_count_by():
    assert count_by(ENTRIES, "status") == {200: 1, 404: 1, 500: 1}
    assert count_by(ENTRIES, "method") == {"GET": 2, "POST": 1}
    assert count_by([], "status") == {}


def test_count_by_on_real_log_file(access_log):
    counts = count_by(parse_entries(read_lines(access_log)), "status")
    number_of_entries = len(list(parse_entries(read_lines(access_log))))

    assert sum(counts.values()) == number_of_entries
