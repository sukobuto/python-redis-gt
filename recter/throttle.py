# from typing import *
import asyncio
from datetime import datetime

from redis import StrictRedis
from uuid import uuid4


class AsyncThrottle:

    def __init__(self, redis: StrictRedis, name: str, max_parallels: int):
        self.redis = redis
        self.name = name
        self.max_parallels = max_parallels

    @property
    def __key(self):
        return 'recter:' + self.name

    async def attend(self, timeout: float) -> bytes:
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
                raise Exception('timeout')

    def exit(self, token):
        self.redis.zrem(self.__key, token)

    async def run_async(self, coroutine, attend_timeout=1.0):
        token = await self.attend(attend_timeout)
        result = await coroutine
        self.exit(token)
        return result
