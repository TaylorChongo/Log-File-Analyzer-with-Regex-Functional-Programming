"""Functional pipeline: map/filter/reduce, partial filters, groupby/islice/takewhile."""

from collections.abc import Callable, Iterable, Iterator
from datetime import datetime
from functools import partial, reduce
from itertools import dropwhile, groupby, islice, takewhile

from logfile_analyzer.parser import parse_line


# --- map: transform ------------------------------------------------------

def parse_entries(lines: Iterable[str]) -> Iterator[dict]:
    """Turn log lines into entry dictionaries, skipping malformed lines."""
    entries = map(parse_line, lines)  # each line -> dict, or None if malformed
    # filter(None, ...) keeps only the items that are not None (or empty).
    return filter(None, entries)


# --- filter: select ------------------------------------------------------

def has_status(status: int, entry: dict) -> bool:
    """Return True if the entry has the given status code."""
    return entry["status"] == status


def has_method(method: str, entry: dict) -> bool:
    """Return True if the entry used the given HTTP method."""
    return entry["method"] == method


def is_error(entry: dict) -> bool:
    """Return True for client and server errors (status 400 and above)."""
    return entry["status"] >= 400


# partial() fills in the first argument ahead of time, giving a new
# function that only needs the entry: is_not_found(entry) == has_status(404, entry)
is_not_found = partial(has_status, 404)
is_post = partial(has_method, "POST")


# --- reduce: aggregate ---------------------------------------------------

def total_bytes(entries: Iterable[dict]) -> int:
    """Add up the size of all entries."""
    # reduce keeps a running total: start at 0, then total + size for each entry.
    return reduce(lambda total, entry: total + entry["size"], entries, 0)


def count_by(entries: Iterable[dict], key: str) -> dict:
    """Count how many entries have each value of a key, e.g. {200: 50, 404: 3}."""

    def add_one(counts: dict, entry: dict) -> dict:
        value = entry[key]
        counts[value] = counts.get(value, 0) + 1
        return counts

    # Start with an empty dictionary and add each entry to it.
    return reduce(add_one, entries, {})


# --- itertools: group, paginate, time range ------------------------------

def group_by(entries: Iterable[dict], key_function: Callable) -> dict:
    """Group entries by the value key_function returns, e.g. {200: [...], 404: [...]}."""
    # groupby only groups items that are NEXT TO each other, so we sort first.
    sorted_entries = sorted(entries, key=key_function)

    groups = {}
    for key, group in groupby(sorted_entries, key=key_function):
        groups[key] = list(group)
    return groups


def group_by_status(entries: Iterable[dict]) -> dict:
    """Group entries by status code: {200: [...], 404: [...]}."""
    return group_by(entries, lambda entry: entry["status"])


def group_by_hour(entries: Iterable[dict]) -> dict:
    """Group entries by the hour of their timestamp: {0: [...], 1: [...], ...}."""
    return group_by(entries, lambda entry: entry["timestamp"].hour)


def paginate(entries: Iterable[dict], page: int, page_size: int) -> Iterator[dict]:
    """Return one page of entries; pages start at 1."""
    start = (page - 1) * page_size
    # islice works like list[start:stop], but on any iterator, lazily.
    return islice(entries, start, start + page_size)


def entries_between(entries: Iterable[dict], start: datetime, end: datetime) -> Iterator[dict]:
    """Return entries with start <= timestamp < end. Entries must be in time order."""
    # dropwhile skips entries until the first one at or after start.
    after_start = dropwhile(lambda entry: entry["timestamp"] < start, entries)
    # takewhile stops at the first entry at or after end, without reading the rest.
    return takewhile(lambda entry: entry["timestamp"] < end, after_start)
