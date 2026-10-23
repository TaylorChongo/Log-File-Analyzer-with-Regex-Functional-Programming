"""Generators and iterators for reading, chaining and batching log files lazily."""

from collections.abc import Iterable, Iterator
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


class BatchIterator:
    """Hand out items in lists (batches) of a fixed size: [1, 2], [3, 4], [5]."""

    def __init__(self, items: Iterable, size: int) -> None:
        # iter() lets us keep taking items from where we stopped last time.
        self.items = iter(items)
        self.size = size

    def __iter__(self) -> "BatchIterator":
        """Return the iterator itself, so it can be used in a for loop."""
        return self

    def __next__(self) -> list:
        """Return the next batch, or raise StopIteration when no items are left."""
        batch = []
        for item in self.items:
            batch.append(item)
            if len(batch) == self.size:
                break

        if not batch:
            raise StopIteration
        return batch
