import asyncio
from datetime import datetime

import pytest
from fakeredis import FakeStrictRedis
from recter.throttle import Throttle


@pytest.fixture(scope="module", autouse=True)
def redis():
    return FakeStrictRedis()


def test_throttle_runs_coroutine(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = Throttle(redis, 'test', 1)
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
    throttle = Throttle(redis, 'test', 1)
    start_at = datetime.now().timestamp()
    start_logs = []

    async def do_something():
        nonlocal start_logs
        start_logs.append((datetime.now().timestamp() - start_at))
        await asyncio.sleep(0.1)

    tasks = [throttle.run_async(do_something()) for _ in range(5)]
    event_loop.run_until_complete(asyncio.wait(tasks))

    start_logs = list(sorted(start_logs))
    last_elapsed = start_logs[0]
    for elapsed in start_logs[1:]:
        assert elapsed - last_elapsed > 0.09
        last_elapsed = elapsed


def test_throttle_works_with_para2(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = Throttle(redis, 'test', 2)

    async def do_something():
        await asyncio.sleep(0.1)

    tasks = [throttle.run_async(do_something()) for _ in range(5)]
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait(tasks))
    assert 0.28 < datetime.now().timestamp() - start_at < 0.32


def test_throttle_works_with_para5(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = Throttle(redis, 'test', 5)

    async def do_something():
        await asyncio.sleep(0.1)

    tasks = [throttle.run_async(do_something()) for _ in range(5)]
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait(tasks))
    assert 0.08 < datetime.now().timestamp() - start_at < 0.12


def test_another_throttles_do_not_conflict(redis, event_loop: asyncio.AbstractEventLoop):
    t1 = Throttle(redis, 'test1', 1)
    t2 = Throttle(redis, 'test2', 1)

    tasks = [
        t1.run_async(asyncio.sleep(0.1)),
        t2.run_async(asyncio.sleep(0.1)),
    ]
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait(tasks))
    assert 0.08 < datetime.now().timestamp() - start_at < 0.12
