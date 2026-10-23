"""Compare a list-based and a generator-based pipeline on a big log file.

Usage (from the project folder):
    python -m scripts.compare_memory

Both versions compute the same thing (total bytes sent), but the list version
loads every line and every entry into memory first, while the generator
version handles one line at a time.
"""

import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path

from logfile_analyzer.parser import parse_line
from logfile_analyzer.pipeline import parse_entries, total_bytes
from logfile_analyzer.readers import read_lines
from scripts.generate_logs import generate

BIG_LOG = Path("reports") / "big.log"
NUMBER_OF_LINES = 100_000


def with_lists(path: Path) -> int:
    """Total bytes using lists: everything is loaded into memory first."""
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = [parse_line(line) for line in lines]
    valid_entries = [entry for entry in entries if entry is not None]
    return sum(entry["size"] for entry in valid_entries)


def with_generators(path: Path) -> int:
    """Total bytes using generators: one line at a time."""
    return total_bytes(parse_entries(read_lines(path)))


def measure(function, path: Path) -> tuple[int, float, int]:
    """Run function(path); return (result, seconds taken, peak memory in bytes)."""
    tracemalloc.start()
    start = time.perf_counter()
    result = function(path)
    seconds = time.perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, seconds, peak


def main() -> None:
    """Create the big log, measure both versions and print a table."""
    start_time = datetime(2026, 10, 20, tzinfo=timezone.utc)
    generate(BIG_LOG, NUMBER_OF_LINES, start_time, seed=42, malformed_rate=0.01)

    list_result, list_seconds, list_peak = measure(with_lists, BIG_LOG)
    gen_result, gen_seconds, gen_peak = measure(with_generators, BIG_LOG)
    assert list_result == gen_result  # both versions must give the same answer

    print()
    print("| Version    | Time (s) | Peak memory (MB) |")
    print("|------------|----------|------------------|")
    print(f"| List       | {list_seconds:8.2f} | {list_peak / 1_000_000:16.2f} |")
    print(f"| Generator  | {gen_seconds:8.2f} | {gen_peak / 1_000_000:16.2f} |")
    print()
    print(f"Generators used {list_peak / gen_peak:.0f}x less memory.")


if __name__ == "__main__":
    main()
