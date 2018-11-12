from typing import *
import asyncio
import math
from asyncio.futures import TimeoutError
from datetime import datetime

from redis import StrictRedis
from uuid import uuid4

from recter.exceptions import WaitingTimeoutError, RunningTimeoutError
from recter.throttle import Throttle


class AsyncThrottle(Throttle):

    async def wait(self, timeout: float) -> bytes:
        token = str(uuid4()).encode('utf8')
        timestamp = datetime.now().timestamp()
        key = self._key
        self.register_as_waiting(token, timeout)
        self.redis.zadd(key, timestamp, token)
        count = 0
        while True:
            cleared = self.redis.zrange(key, 0, self.max_parallels - 1)
            if token in cleared:
                return token
            await asyncio.sleep(self.polling_interval)
            count += 1
            if count % self.garbage_check_interval_count == 0:
                self.remove_garbage(cleared)
            if datetime.now().timestamp() - timestamp > timeout:
                self.exit(token)
                raise WaitingTimeoutError()

    async def run(self, coroutine, waiting_timeout=10.0, running_timeout=10.0):
        token = await self.wait(waiting_timeout)
        try:
            self.register_as_running(token, running_timeout)
            return await asyncio.wait_for(coroutine, running_timeout)
        except TimeoutError as te:
            raise RunningTimeoutError(te)
        finally:
            self.exit(token)
