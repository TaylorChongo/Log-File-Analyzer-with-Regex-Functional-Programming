"""Tests for the decorators and the lru_cache on strip_query_string."""

from logfile_analyzer.decorators import log_call, timer
from logfile_analyzer.patterns import strip_query_string


def test_timer_returns_result_and_prints_time(capsys):
    @timer
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    assert "[timer] add took" in capsys.readouterr().out


def test_log_call_prints_name_and_arguments(capsys):
    @log_call
    def add(a, b):
        return a + b

    assert add(1, b=2) == 3
    assert "calling add with args=(1,) kwargs={'b': 2}" in capsys.readouterr().out


def test_chained_decorators(capsys):
    @timer
    @log_call
    def add(a, b):
        return a + b

    assert add(1, 2) == 3
    output = capsys.readouterr().out
    assert "[log_call] calling add" in output
    assert "[timer] add took" in output
    assert add.__name__ == "add"  # kept thanks to @wraps


def test_strip_query_string_uses_cache():
    strip_query_string.cache_clear()

    strip_query_string("/products/107?ref=home")  # first time: computed
    strip_query_string("/products/107?ref=home")  # second time: from the cache

    info = strip_query_string.cache_info()
    assert info.misses == 1
    assert info.hits == 1
