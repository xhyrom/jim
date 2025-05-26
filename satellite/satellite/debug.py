from functools import wraps
from logging import Logger
from time import perf_counter_ns
from typing import Any, Callable
import asyncio


def format_time(ns: int) -> str:
    if ns < 1_000:
        return f"{ns} ns"
    elif ns < 1_000_000:
        return f"{ns / 1_000:.2f} µs"
    elif ns < 1_000_000_000:
        return f"{ns / 1_000_000:.2f} ms"
    else:
        return f"{ns / 1_000_000_000:.2f} s"


def time_me(func: Callable | None = None, *, name: str | None = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter_ns()
            result = func(*args, **kwargs)
            end = perf_counter_ns()

            duration_ns = end - start
            formatted_time = format_time(duration_ns)
            func_name = name or func.__name__

            print(f"{func_name} \033[93mtook\033[0m \033[96m{formatted_time}\033[0m")

            return result

        return wrapper

    if func is None:
        return decorator
    return decorator(func)


def sneaky_throws(
    func: Callable | None = None,
    *,
    logger: Logger | None = None,
    retry_delay: float = 1.0,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            while True:
                try:
                    sneaky_throws(await func(*args, **kwargs))
                except Exception as e:
                    if logger:
                        logger.exception(f"Error in {func.__name__}: {str(e)}")

                    await asyncio.sleep(retry_delay)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return sneaky_throws(func(*args, **kwargs))
            except Exception as e:
                if logger:
                    logger.exception(f"Error in {func.__name__}: {str(e)}")
                import time

                time.sleep(retry_delay)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    if func is None:
        return decorator
    return decorator(func)
