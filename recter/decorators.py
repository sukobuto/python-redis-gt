import asyncio
from functools import wraps

from redis import StrictRedis

from .async_throttle import AsyncThrottle
from .throttle import Throttle


def throttle(name: str, parallels: int, waiting_timeout=10.0, running_timeout=10.0, redis: StrictRedis = None,
             polling_interval=0.01, garbage_check_window=3, garbage_check_interval_count=10):
    def _throttle(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_inner(*args, **kwargs):
                at = AsyncThrottle(redis, name, parallels,
                                   polling_interval, garbage_check_window, garbage_check_interval_count)
                return await at.run(func(*args, **kwargs),
                                    waiting_timeout=waiting_timeout, running_timeout=running_timeout)
            return async_inner
        else:
            @wraps(func)
            def inner(*args, **kwargs):
                t = Throttle(redis, name, parallels,
                             polling_interval, garbage_check_window, garbage_check_interval_count)
                return t.run(func, *args, **kwargs,
                             waiting_timeout=waiting_timeout, running_timeout=running_timeout)
            return inner
    return _throttle
