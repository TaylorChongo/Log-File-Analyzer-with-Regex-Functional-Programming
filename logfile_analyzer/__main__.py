"""Command-line entry point: python -m logfile_analyzer <logfile> [<logfile> ...]."""

import sys
from pathlib import Path

from logfile_analyzer.report import build_report, load_entries

REPORT_FILE = Path("reports") / "report.txt"


def main() -> None:
    """Analyze the log files given on the command line and save the report."""
    paths = sys.argv[1:]  # everything typed after "python -m logfile_analyzer"
    if not paths:
        print("usage: python -m logfile_analyzer <logfile> [<logfile> ...]")
        sys.exit(1)

    entries, lines_read = load_entries(paths)
    report = build_report(entries, lines_read)

    print()
    print(report)

    REPORT_FILE.parent.mkdir(exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"\nReport saved to {REPORT_FILE}")


if __name__ == "__main__":
    main()
