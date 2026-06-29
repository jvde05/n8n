"""Ustel geri cekilmeli (exponential backoff) retry dekoratoru.

Aglar/3. parti API'ler gecici hata verir; bunu merkezi olarak yonetiriz.
"""
import functools
import time
from typing import Callable, Tuple, Type

from .logging_utils import get_logger

log = get_logger("retry")


def retry(
    times: int = 3,
    base_delay: float = 1.0,
    factor: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable:
    """times denemesi yapar; her basarisizlikta base*factor^n bekler."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last = None
            for attempt in range(1, times + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:  # noqa: BLE001
                    last = exc
                    if attempt == times:
                        break
                    log.warning(
                        "%s basarisiz (deneme %d/%d): %s — %.1fs sonra tekrar",
                        fn.__name__, attempt, times, exc, delay,
                    )
                    time.sleep(delay)
                    delay *= factor
            raise last

        return wrapper

    return decorator
