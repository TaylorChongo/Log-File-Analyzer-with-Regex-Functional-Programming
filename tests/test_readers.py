"""Tests for the generators in logfile_analyzer.readers."""

import types

import pytest

from logfile_analyzer.readers import BatchIterator, read_lines, read_many


def test_read_lines_is_a_generator(sample_log):
    assert isinstance(read_lines(sample_log), types.GeneratorType)


def test_read_lines_yields_each_line_without_newline(sample_log, valid_line):
    lines = list(read_lines(sample_log))

    assert len(lines) == 8  # 5 valid lines + 3 malformed lines
    assert lines[0] == valid_line


def test_read_lines_is_lazy(tmp_path):
    # Nothing runs until we ask for the first line, so a missing file
    # only raises an error at next(), not when the generator is created.
    lines = read_lines(tmp_path / "missing.log")

    with pytest.raises(FileNotFoundError):
        next(lines)


def test_read_lines_can_only_be_used_once(sample_log):
    lines = read_lines(sample_log)

    assert len(list(lines)) == 8
    assert list(lines) == []


def test_read_many_chains_files_in_order(tmp_path):
    first = tmp_path / "first.log"
    second = tmp_path / "second.log"
    first.write_text("a1\na2\n", encoding="utf-8")
    second.write_text("b1\n", encoding="utf-8")

    assert list(read_many([first, second])) == ["a1", "a2", "b1"]


def test_batch_iterator_splits_items_into_batches():
    batches = list(BatchIterator([1, 2, 3, 4, 5], 2))

    assert batches == [[1, 2], [3, 4], [5]]


def test_batch_iterator_with_no_items():
    assert list(BatchIterator([], 3)) == []


def test_batch_iterator_works_with_a_generator(sample_log):
    batches = list(BatchIterator(read_lines(sample_log), 3))

    assert [len(batch) for batch in batches] == [3, 3, 2]
