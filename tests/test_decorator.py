import asyncio
import threading
import time
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import List

import pytest
from fakeredis import FakeStrictRedis
from redis import StrictRedis

from redis_gt import Throttle, WaitingTimeoutError
from redis_gt.decorators import throttle as throttle_decorator


@pytest.fixture(scope="module", autouse=True)
def redis():
    return FakeStrictRedis()


def await_threads(threads: List[threading.Thread]) -> List[threading.Thread]:
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return threads


def test_throttle_runs_coroutine(redis, event_loop: AbstractEventLoop):

    @throttle_decorator('test', 1, redis=redis)
    async def do_something(a, b):
        await asyncio.sleep(0.1)
        return a * b

    assert event_loop.run_until_complete(do_something(3, 7)) == 21


def test_async_throttle_works_with_para2(redis, event_loop: asyncio.AbstractEventLoop):

    @throttle_decorator('test', 2, redis=redis)
    async def do_something():
        await asyncio.sleep(0.1)

    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait([do_something() for _ in range(5)]))
    assert 0.3 <= datetime.now().timestamp() - start_at < 0.35
    assert not redis.exists('redis_gt:test')


def test_throttle_works_with_para5(redis):

    @throttle_decorator('test', 5, redis=redis)
    def do_nothing():
        time.sleep(0.1)

    threads = [threading.Thread(target=do_nothing) for _ in range(10)]
    start_at = datetime.now().timestamp()
    await_threads(threads)
    assert 0.2 <= datetime.now().timestamp() - start_at < 0.25
    assert not redis.exists('redis_gt:test')


def test_default_redis(redis):
    Throttle.default_redis = redis

    @throttle_decorator('test', 2)
    def do_something():
        return 'hello'

    assert do_something() == 'hello'
