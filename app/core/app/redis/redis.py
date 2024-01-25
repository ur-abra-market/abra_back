from redis import Redis

from core.settings import redis_settings

redis_connection: Redis = Redis.from_url(
    url=f"redis://{redis_settings.HOST}:{redis_settings.PORT}/0",
    password=redis_settings.PASSWORD,
)
