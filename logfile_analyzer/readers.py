"""Generators and iterators for reading, chaining and batching log files lazily."""

from collections.abc import Iterator
from itertools import chain
from pathlib import Path


def read_lines(path: str | Path) -> Iterator[str]:
    """Yield the lines of a file one at a time, without the trailing newline."""
    with open(path, encoding="utf-8") as file:
        for line in file:
            yield line.rstrip("\n")


def read_many(paths: list[str | Path]) -> Iterator[str]:
    """Yield the lines of several files, one file after another."""
    # Creating the generators does not open any file yet;
    # each file is only opened when chain() reaches it.
    generators = [read_lines(path) for path in paths]
    return chain(*generators)
