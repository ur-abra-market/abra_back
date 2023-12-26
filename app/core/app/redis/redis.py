from redis import Redis

from core.settings import redis_settings

redis_connection: Redis = Redis.from_url(
    url=f"redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/0",
    password=redis_settings.REDIS_PASSWORD,
)
