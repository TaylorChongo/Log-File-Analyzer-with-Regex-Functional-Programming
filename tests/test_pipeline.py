"""Tests for the functional pipeline in logfile_analyzer.pipeline."""

from datetime import datetime, timezone

from logfile_analyzer.pipeline import (
    count_by,
    entries_between,
    group_by_hour,
    group_by_status,
    has_method,
    has_status,
    is_error,
    is_not_found,
    is_post,
    paginate,
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


def at_hour(hour):
    """Make an entry with a timestamp on 20 Oct 2026 at the given hour."""
    return {"timestamp": datetime(2026, 10, 20, hour, 0, tzinfo=timezone.utc)}


def test_group_by_status():
    groups = group_by_status([GET_OK, GET_NOT_FOUND, GET_OK])

    assert groups == {200: [GET_OK, GET_OK], 404: [GET_NOT_FOUND]}


def test_group_by_hour():
    groups = group_by_hour([at_hour(5), at_hour(1), at_hour(5)])

    assert list(groups) == [1, 5]
    assert len(groups[5]) == 2


def test_group_by_hour_on_real_log_file(access_log):
    groups = group_by_hour(parse_entries(read_lines(access_log)))

    assert all(0 <= hour <= 23 for hour in groups)


def test_paginate():
    items = list(range(10))  # 0, 1, ..., 9

    assert list(paginate(items, page=1, page_size=3)) == [0, 1, 2]
    assert list(paginate(items, page=2, page_size=3)) == [3, 4, 5]
    assert list(paginate(items, page=4, page_size=3)) == [9]
    assert list(paginate(items, page=5, page_size=3)) == []


def test_entries_between():
    entries = [at_hour(hour) for hour in range(6)]  # hours 0 to 5, in order
    start = datetime(2026, 10, 20, 2, 0, tzinfo=timezone.utc)
    end = datetime(2026, 10, 20, 4, 0, tzinfo=timezone.utc)

    selected = list(entries_between(entries, start, end))

    assert selected == [at_hour(2), at_hour(3)]
