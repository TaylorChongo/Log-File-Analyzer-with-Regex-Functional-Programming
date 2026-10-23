"""Function decorators: @timer, @log_call, and lru_cache-based caching."""

import time
from functools import wraps


def timer(func):
    """Print how long the decorated function took to run."""

    # @wraps keeps the original function's name, so messages show
    # "build_report" instead of "wrapper".
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f} seconds")
        return result

    return wrapper


def log_call(func):
    """Print the function's name and arguments every time it is called."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[log_call] calling {func.__name__} with args={args} kwargs={kwargs}")
        return func(*args, **kwargs)

    return wrapper
