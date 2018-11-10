import asyncio
from datetime import datetime
from pprint import pprint

import pytest
from fakeredis import FakeStrictRedis
from recter.throttle import Throttle


@pytest.fixture(scope="module", autouse=True)
def redis():
    return FakeStrictRedis()


def test_fakeredis_zrem(redis):
    redis.zadd('test', 1.1, 'AAA')
    print(redis.zrange('test', 0, -1))
    assert redis.zrem('test', 'AAA') == 1
    assert redis.zrem('test', 'AAA') == 0
    print(redis.zrange('test', 0, -1))
    assert redis.zrange('test', 0, -1) == []


def test_throttle_runs_coroutine(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = Throttle(redis, 1)
    done = False

    async def do_something(a, b):
        nonlocal done
        await asyncio.sleep(0.1)
        done = True
        return a * b

    coroutine = do_something(3, 7)
    assert not done
    assert event_loop.run_until_complete(throttle.run_async(coroutine)) == 21
    assert done


def test_throttle_works_with_para1(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = Throttle(redis, 1)
    start_at = datetime.now().timestamp()
    start_logs = []

    async def do_something():
        nonlocal start_logs
        start_logs.append((datetime.now().timestamp() - start_at))
        await asyncio.sleep(0.1)

    tasks = [throttle.run_async(do_something()) for n in range(5)]
    event_loop.run_until_complete(asyncio.wait(tasks))

    start_logs = list(sorted(start_logs))
    pprint(start_logs)
    last_elapsed = start_logs[0]
    for elapsed in start_logs[1:]:
        assert elapsed - last_elapsed > 0.09
        last_elapsed = elapsed
