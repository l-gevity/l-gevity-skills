import time


def with_retry(fn, attempts=3, delay=1.0):
    """Call fn, retrying on any exception with a fixed delay."""
    for attempt in range(attempts):
        try:
            return fn()
        except Exception:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
