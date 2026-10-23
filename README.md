# Log File Analyzer

Parses Apache/Nginx access logs (Combined Log Format) with regular expressions and
analyzes them using functional programming, generators, `itertools`/`functools`,
and decorators.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

The sample logs `data/access.log` (1500 lines) and `data/access_2.log` (1000 lines) are
included. To recreate them: `python scripts/generate_logs.py`.

## Usage

```bash
python -m logfile_analyzer data/access.log data/access_2.log   # print + save reports/report.txt
python -m scripts.compare_memory                                 # generator vs. list demo
pytest                                                           # run the test suite
mypy logfile_analyzer                                            # type check
```

Example output (shortened):

```
[log_call] calling load_entries with args=(['data/access.log', 'data/access_2.log'],) kwargs={}
processed 500 lines...
...
processed 2500 lines...
[timer] load_entries took 0.0477 seconds
[timer] build_report took 0.0035 seconds

=== Log File Analysis Report ===

Lines read:         2500
Parsed entries:     2471
Malformed lines:    29
Errors (4xx/5xx):   516
Not found (404):    171
POST requests:      477
Total bytes sent:   72,192,653
...
```

The full report also lists requests per status code, the top 5 pages and IP addresses,
requests per hour, and the first page of errors.

## Project Structure

```
logfile_analyzer/
  patterns.py    compiled regexes (log line, IP, URL, email) + cleaning with re.sub
  parser.py      raw line -> dict via named groups
  readers.py     generators: lazy file reading, chain() of files, batching iterator
  pipeline.py    map/filter/reduce, partial() filters, groupby/islice/takewhile
  decorators.py  @timer and @log_call
  report.py      loads entries in batches and builds the report
  __main__.py    CLI entry point
scripts/generate_logs.py   sample log generator
scripts/compare_memory.py  generator vs. list memory demo
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

All patterns live in `logfile_analyzer/patterns.py` and are compiled once with `re.compile`.

### `LOG_PATTERN`: one log line

Each `(?P<name>...)` is a **named group**, so a field is read by name: `match["status"]`.

| Part | Matches | Example |
|---|---|---|
| `(?P<ip>\d{1,3}(?:\.\d{1,3}){3})` | 4 groups of 1-3 digits separated by dots | `192.168.1.10` |
| `\S+ \S+` | ident and user fields (ignored) | `- -` |
| `\[(?P<timestamp>\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} [+-]\d{4})\]` | date, time and timezone inside `[ ]` | `[21/Oct/2026:14:22:01 +0000]` |
| `"(?P<method>[A-Z]+) (?P<url>\S+) (?P<protocol>[^"]+)"` | the request inside quotes | `"GET /index.html HTTP/1.1"` |
| `(?P<status>\d{3})` | exactly 3 digits | `200` |
| `(?P<size>\d+\|-)` | a number, or `-` when nothing was sent | `5120` |
| `"(?P<referrer>[^"]*)"` | anything except a quote (may be empty) | `"-"` |
| `"(?P<user_agent>[^"]*)"` | anything except a quote | `"Mozilla/5.0 ..."` |

Lines that do not match (empty lines, broken dates, non-numeric status) return `None`
and are skipped by the parser.

### Validation patterns

| Pattern | Idea | Valid | Invalid |
|---|---|---|---|
| `IP_PATTERN` | 4 octets, each `25[0-5]\|2[0-4]\d\|1?\d?\d` (0-255) | `192.168.1.10` | `256.1.1.1`, `192.168.1` |
| `URL_PATTERN` | `https?://` + domain `[\w.-]+` + optional path `(?:/\S*)?` | `https://example.com/about` | `www.google.com` |
| `EMAIL_PATTERN` | name `[\w.+-]+` @ domain with at least one `.ext` | `user@example.com` | `user@example` |

`is_valid_ip`, `is_valid_url` and `is_valid_email` use `fullmatch`, so the **whole** text
must match.

### `re` functions used

| Function | Where | Purpose |
|---|---|---|
| `match` | `parse_line` | does the line start with a valid log entry? |
| `fullmatch` | `is_valid_*` | is the whole text valid? |
| `search` | `find_first_ip` | first IP anywhere in a text |
| `findall` | `find_ips` | every IP in a text |
| `sub` | `strip_query_string`, `mask_ip` | data cleaning: `/products/107?ref=home` -> `/products/107`, `192.168.1.16` -> `192.168.1.xxx` |

## Functional Pipeline

Every step is lazy: one line flows through the whole pipeline before the next line is read.

```
 data/access.log ─┐
                  ├─ chain() ──> read_lines()  (yield, one line at a time)
 data/access_2.log┘                  │
                                     ▼
                          BatchIterator(500)   (custom iterator, progress output)
                                     │
                                     ▼
                     map(parse_line)  ──>  filter(None)      line -> dict, drop malformed
                                     │
                                     ▼
          ┌──────────────┬───────────┼──────────────┬──────────────────┐
          ▼              ▼           ▼              ▼                  ▼
   filter(is_error)  reduce:     reduce:      groupby (by hour)   islice (paginate)
   filter(is_not_    total_bytes count_by     sorted first        first 5 errors
   found / is_post)              status/IP/URL
   (partial)
          └──────────────┴───────────┼──────────────┴──────────────────┘
                                     ▼
                              build_report()  ──>  terminal + reports/report.txt
```

| Step | Tool | Code |
|---|---|---|
| Read | generator (`yield`), `itertools.chain` | `read_lines`, `read_many` |
| Batch | custom iterator (`__iter__` / `__next__`) | `BatchIterator` |
| Transform | `map` | `parse_entries`, `with_clean_url` |
| Select | `filter` + `functools.partial` | `is_error`, `is_not_found = partial(has_status, 404)`, `is_post` |
| Aggregate | `functools.reduce` | `total_bytes`, `count_by` |
| Group | `itertools.groupby` (after sorting) | `group_by_status`, `group_by_hour` |
| Paginate | `itertools.islice` | `paginate` |
| Time range | `itertools.dropwhile` + `takewhile` | `entries_between` (stops reading after `end`) |
| Decorate | `@timer`, `@log_call` (chained), `@lru_cache` | `load_entries`, `build_report`, `strip_query_string` |

Example of a chained pipeline:

```python
not_found = filter(is_not_found, parse_entries(read_lines("data/access.log")))
```

## Generator vs. List Performance

`python -m scripts.compare_memory` generates a 100,000-line log and computes the total
bytes sent in two ways:

- **List:** read the whole file into a list, parse into a list, filter into a list, then sum.
- **Generator:** `total_bytes(parse_entries(read_lines(path)))`, one line at a time.

Peak memory is measured with `tracemalloc` and time with `time.perf_counter`.

| Version | Time (s) | Peak memory (MB) |
|---|---|---|
| List | 14.89 | 92.21 |
| Generator | 9.21 | 0.15 |

Both versions return the same total. The generator version used **about 600x less memory**,
and its memory does not grow with the file size, while the list version grows with every
line. (Times are high because `tracemalloc` slows Python down; it affects both versions.)

The test `test_generator_memory_stays_flat_as_file_grows` checks the same behaviour
automatically.

## Testing

```bash
pytest
```

46 tests cover the regex patterns, the parser, the generators and batching iterator,
the functional pipeline, the decorators, the report, and generator memory usage.
