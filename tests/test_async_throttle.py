import asyncio
from datetime import datetime

import pytest
from fakeredis import FakeStrictRedis
from redis import StrictRedis

from recter import AsyncThrottle, WaitingTimeoutError, RunningTimeoutError


@pytest.fixture(scope="module", autouse=True)
def redis():
    return FakeStrictRedis()


def test_throttle_runs_coroutine(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = AsyncThrottle(redis, 'test', 1)
    done = False

    async def do_something(a, b):
        nonlocal done
        await asyncio.sleep(0.1)
        done = True
        return a * b

    coroutine = do_something(3, 7)
    assert not done
    assert event_loop.run_until_complete(throttle.run(coroutine)) == 21
    assert done
    assert not redis.exists('recter:test')


def test_throttle_works_with_para1(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = AsyncThrottle(redis, 'test', 1)
    start_at = datetime.now().timestamp()
    start_logs = []

    async def do_something():
        nonlocal start_logs
        start_logs.append((datetime.now().timestamp() - start_at))
        await asyncio.sleep(0.1)

    tasks = [throttle.run(do_something()) for _ in range(5)]
    event_loop.run_until_complete(asyncio.wait(tasks))

    start_logs = list(sorted(start_logs))
    assert len(start_logs) == 5
    last_elapsed = start_logs[0]
    for elapsed in start_logs[1:]:
        assert elapsed - last_elapsed >= 0.1
        last_elapsed = elapsed
    assert not redis.exists('recter:test')


def test_throttle_works_with_para2(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = AsyncThrottle(redis, 'test', 2)
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait([throttle.run(asyncio.sleep(0.1)) for _ in range(5)]))
    assert 0.3 <= datetime.now().timestamp() - start_at < 0.35
    assert not redis.exists('recter:test')


def test_throttle_works_with_para5(redis, event_loop: asyncio.AbstractEventLoop):
    throttle = AsyncThrottle(redis, 'test', 5)
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait([throttle.run(asyncio.sleep(0.1)) for _ in range(5)]))
    assert 0.1 <= datetime.now().timestamp() - start_at < 0.13
    assert not redis.exists('recter:test')


def test_another_throttles_do_not_conflict(redis, event_loop: asyncio.AbstractEventLoop):
    t1 = AsyncThrottle(redis, 'test1', 1)
    t2 = AsyncThrottle(redis, 'test2', 1)
    start_at = datetime.now().timestamp()
    event_loop.run_until_complete(asyncio.wait([
        t1.run(asyncio.sleep(0.1)),
        t2.run(asyncio.sleep(0.1)),
    ]))
    assert 0.1 <= datetime.now().timestamp() - start_at < 0.13
    assert not redis.exists('recter:test1')
    assert not redis.exists('recter:test2')


@pytest.mark.asyncio
async def test_throttle_raises_waiting_timeout_error_when_waiting_has_timeout(redis):
    throttle = AsyncThrottle(redis, 'test', 1)
    done_tasks, _ = await asyncio.wait([
        throttle.run(asyncio.sleep(0.1), waiting_timeout=0.05),
        throttle.run(asyncio.sleep(0.1), waiting_timeout=0.05),
    ])
    with pytest.raises(WaitingTimeoutError):
        for task in done_tasks:
            task.result()
    assert not redis.exists('recter:test')


@pytest.mark.asyncio
async def test_throttle_raises_running_timeout_error_when_running_has_timeout(redis: StrictRedis):
    throttle = AsyncThrottle(redis, 'test', 1)
    with pytest.raises(RunningTimeoutError):
        await throttle.run(asyncio.sleep(0.1), running_timeout=0.05)
    assert not redis.exists('recter:test')


@pytest.mark.asyncio
async def test_throttle_removes_garbage_token(redis: StrictRedis):
    throttle = AsyncThrottle(redis, 'test', 1)
    garbage_token = await throttle.wait(1.0)
    assert redis.zscore('recter:test', garbage_token)
    await throttle.run(asyncio.sleep(0.01))
    assert not redis.exists('recter:test')
