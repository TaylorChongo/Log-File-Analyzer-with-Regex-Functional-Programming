"""Functional pipeline: map/filter/reduce, partial filters, groupby/islice/takewhile."""

from collections.abc import Iterable, Iterator
from functools import partial, reduce

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
