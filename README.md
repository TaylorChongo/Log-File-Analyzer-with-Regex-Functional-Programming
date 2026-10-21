# Log File Analyzer

Parses Apache/Nginx access logs (Combined Log Format) with regular expressions and
analyzes them using functional programming, generators, `itertools`/`functools`,
and decorators.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
python scripts/generate_logs.py # creates data/access.log (1500) + data/access_2.log (1000)
```

## Usage

```bash
python -m logfile_analyzer data/access.log data/access_2.log
pytest
mypy logfile_analyzer
```

## Project Structure

```
logfile_analyzer/
  patterns.py    compiled regexes (log line, IP, URL, email) + cleaning with re.sub
  parser.py      raw line -> dict via named groups
  readers.py     generators: lazy file reading, chain() of files, batching iterator
  pipeline.py    map/filter/reduce, partial() filters, groupby/islice/takewhile
  decorators.py  @timer, @log_call, lru_cache caching
  report.py      analytics report output
  __main__.py    CLI entry point
scripts/generate_logs.py   sample log generator
data/                      sample logs
tests/                     pytest suite
reports/                   generated reports (git-ignored)
```

## Log Format

```
192.168.1.10 - - [21/Oct/2026:14:22:01 +0000] "GET /index.html HTTP/1.1" 200 5120 "-" "Mozilla/5.0 ..."
<ip>       <ident> <user> [<timestamp>]  "<method> <url> <protocol>" <status> <size> "<referrer>" "<user agent>"
```

The sample logs include ~1% malformed lines to exercise error handling.

## Regex Pattern Explanations

_TODO_

## Functional Pipeline

_TODO: pipeline diagram (read -> parse -> filter -> group/aggregate -> report)_

## Generator vs. List Performance

_TODO: time and memory (tracemalloc) comparison table_
