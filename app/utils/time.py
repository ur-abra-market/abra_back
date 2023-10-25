import time
from functools import wraps

from logger import logger


def exec_time(title: str = None):
    def function(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            end_time = time.perf_counter()

            class_name = args[0].__class__.__name__ if args else None

            logger.info(
                f"{title or class_name or  f'Execution of {func.__name__}'} ended in {end_time-start_time:.3f} seconds"
            )
            return result

        return wrapper

    return function
