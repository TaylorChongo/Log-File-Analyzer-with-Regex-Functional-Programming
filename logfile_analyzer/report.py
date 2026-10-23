"""Build and print analytics reports from parsed log entries."""

from pathlib import Path

from logfile_analyzer.decorators import log_call, timer
from logfile_analyzer.patterns import strip_query_string
from logfile_analyzer.pipeline import (
    count_by,
    group_by_hour,
    is_error,
    is_not_found,
    is_post,
    paginate,
    parse_entries,
    total_bytes,
)
from logfile_analyzer.readers import BatchIterator, read_many

BATCH_SIZE = 500


@timer
@log_call
def load_entries(paths: list[str | Path]) -> tuple[list[dict], int]:
    """Read and parse all files in batches; return (entries, number of lines read)."""
    entries: list[dict] = []
    lines_read = 0
    for batch in BatchIterator(read_many(paths), BATCH_SIZE):
        lines_read += len(batch)
        entries.extend(parse_entries(batch))
        print(f"processed {lines_read} lines...")
    return entries, lines_read


def top_n(counts: dict, n: int) -> list[tuple]:
    """Return the n (value, count) pairs with the highest counts."""
    return sorted(counts.items(), key=lambda pair: pair[1], reverse=True)[:n]


def with_clean_url(entry: dict) -> dict:
    """Return a small dict holding the entry's URL without its query string."""
    return {"url": strip_query_string(entry["url"])}


@timer
def build_report(entries: list[dict], lines_read: int) -> str:
    """Build the analytics report as text."""
    # entries is a list (not a generator) because we go through it many times.
    errors = list(filter(is_error, entries))
    pages = count_by(map(with_clean_url, entries), "url")

    lines = [
        "=== Log File Analysis Report ===",
        "",
        f"Lines read:         {lines_read}",
        f"Parsed entries:     {len(entries)}",
        f"Malformed lines:    {lines_read - len(entries)}",
        f"Errors (4xx/5xx):   {len(errors)}",
        f"Not found (404):    {len(list(filter(is_not_found, entries)))}",
        f"POST requests:      {len(list(filter(is_post, entries)))}",
        f"Total bytes sent:   {total_bytes(entries):,}",
        "",
        "Requests per status code:",
    ]
    for status, count in sorted(count_by(entries, "status").items()):
        lines.append(f"  {status}: {count}")

    lines += ["", "Top 5 pages:"]
    for url, count in top_n(pages, 5):
        lines.append(f"  {count:5}  {url}")

    lines += ["", "Top 5 IP addresses:"]
    for ip, count in top_n(count_by(entries, "ip"), 5):
        lines.append(f"  {count:5}  {ip}")

    lines += ["", "Requests per hour:"]
    for hour, hour_entries in group_by_hour(entries).items():
        lines.append(f"  {hour:02}:00  {len(hour_entries)}")

    lines += ["", "First 5 errors (page 1):"]
    for entry in paginate(errors, page=1, page_size=5):
        lines.append(f"  {entry['timestamp']}  {entry['status']}  {entry['method']} {entry['url']}")

    return "\n".join(lines)
