# from typing import *
import asyncio
from datetime import datetime

from redis import StrictRedis
from uuid import uuid4


class Throttle:

    def __init__(self, redis: StrictRedis, max_parallels: int):
        self.redis = redis
        self.max_parallels = max_parallels

    @property
    def __key(self):
        return 'recter'

    async def run_async(self, coroutine):
        # return await coroutine
        key = self.__key
        token = str(uuid4()).encode('utf8')
        timestamp = datetime.now().timestamp()
        self.redis.zadd(key, timestamp, token)
        limit = 100
        while True:
            cleared = self.redis.zrange(key, 0, self.max_parallels - 1)
            if token in cleared:
                break
            limit -= 1
            if limit <= 0:
                raise Exception('retry limit over')
            await asyncio.sleep(0.05)
        result = await coroutine
        self.redis.zrem(key, token)
        return result
