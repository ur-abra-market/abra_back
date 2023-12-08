from rq import Queue

from core.settings import tests_settings
from redisq import redis_connection

is_async = tests_settings.TESTS_RUNNING

default_queue: Queue = Queue(
    is_async=is_async,
    name="default",
    connection=redis_connection,
)
