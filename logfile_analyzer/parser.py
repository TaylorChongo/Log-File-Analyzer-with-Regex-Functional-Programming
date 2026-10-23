"""Turn raw log lines into structured dictionaries using named-group regexes."""

from datetime import datetime

from logfile_analyzer.patterns import LOG_PATTERN

# How the timestamp is written in the log: 21/Oct/2026:14:22:01 +0000
#   %d day, %b month name, %Y year, %H:%M:%S time, %z timezone
TIMESTAMP_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_line(line: str) -> dict | None:
    """Turn one log line into a dictionary, or return None if the line is malformed."""
    match = LOG_PATTERN.match(line)
    if match is None:
        return None

    # "-" means no body was sent, so we count it as 0 bytes.
    size = 0 if match["size"] == "-" else int(match["size"])

    return {
        "ip": match["ip"],
        "timestamp": datetime.strptime(match["timestamp"], TIMESTAMP_FORMAT),
        "method": match["method"],
        "url": match["url"],
        "protocol": match["protocol"],
        "status": int(match["status"]),
        "size": size,
        "referrer": match["referrer"],
        "user_agent": match["user_agent"],
    }
