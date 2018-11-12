# from typing import *
import asyncio
from asyncio.futures import TimeoutError
from datetime import datetime

from redis import StrictRedis
from uuid import uuid4

from recter.exceptions import WaitingTimeoutError, RunningTimeoutError


class AsyncThrottle:

    def __init__(self, redis: StrictRedis, name: str, max_parallels: int):
        self.redis = redis
        self.name = name
        self.max_parallels = max_parallels

    @property
    def __key(self):
        return 'recter:' + self.name

    async def wait(self, timeout: float) -> bytes:
        token = str(uuid4()).encode('utf8')
        timestamp = datetime.now().timestamp()
        key = self.__key
        self.redis.zadd(key, timestamp, token)
        while True:
            cleared = self.redis.zrange(key, 0, self.max_parallels - 1)
            if token in cleared:
                return token
            await asyncio.sleep(0.01)
            if datetime.now().timestamp() - timestamp > timeout:
                self.exit(token)
                raise WaitingTimeoutError()

    def exit(self, token):
        self.redis.zrem(self.__key, token)

    async def run(self, coroutine, waiting_timeout=10.0, running_timeout=10.0):
        token = await self.wait(waiting_timeout)
        try:
            result = await asyncio.wait_for(coroutine, running_timeout)
            return result
        except TimeoutError as te:
            raise RunningTimeoutError(te)
        finally:
            self.exit(token)
