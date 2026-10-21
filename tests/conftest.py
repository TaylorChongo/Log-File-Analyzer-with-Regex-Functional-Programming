"""Shared pytest fixtures."""

from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

VALID_LINE = (
    '192.168.1.10 - - [21/Oct/2026:14:22:01 +0000] "GET /index.html HTTP/1.1" '
    '200 5120 "-" "Mozilla/5.0 (X11; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"'
)
MALFORMED_LINES = [
    "",
    "this is not a log line",
    '999.1.1 - - [bad date] "GET / HTTP/1.1" 200 12',
]


@pytest.fixture
def valid_line() -> str:
    return VALID_LINE


@pytest.fixture
def malformed_lines() -> list[str]:
    return list(MALFORMED_LINES)


@pytest.fixture
def sample_log(tmp_path: Path) -> Path:
    """A tiny log file on disk for generator/reader tests."""
    path = tmp_path / "sample.log"
    path.write_text("\n".join([VALID_LINE] * 5 + MALFORMED_LINES) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def access_log() -> Path:
    return DATA_DIR / "access.log"
