import redis


class Defaults:
    redis = None
    redis_url = 'redis://127.0.0.1:6379'

    @classmethod
    def get_redis(cls):
        if cls.redis is not None:
            return cls.redis
        return redis.StrictRedis.from_url(cls.redis_url)
