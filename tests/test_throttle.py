import threading
import time
from datetime import datetime
from typing import List

import pytest
from fakeredis import FakeStrictRedis
from redis import StrictRedis

from redis_gt import Throttle, WaitingTimeoutError


@pytest.fixture(scope="module", autouse=True)
def redis():
    return FakeStrictRedis()


def await_threads(threads: List[threading.Thread]) -> List[threading.Thread]:
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    return threads


def test_throttle_runs_function(redis):
    throttle = Throttle('test', 1, redis)
    done = False

    def do_something(a, b):
        nonlocal done
        time.sleep(0.1)
        done = True
        return a * b

    assert not done
    assert throttle.run(do_something, 3, 7) == 21
    assert done
    assert not redis.exists('redis_gt:test')


def test_throttle_works_with_para1(redis):
    start_at = datetime.now().timestamp()
    start_logs = []

    def do_something():
        nonlocal start_logs
        start_logs.append((datetime.now().timestamp() - start_at))
        time.sleep(0.1)

    def do_something_with_throttle():
        throttle = Throttle('test', 1, redis)
        throttle.run(do_something)

    threads = [threading.Thread(target=do_something_with_throttle) for _ in range(5)]
    await_threads(threads)

    start_logs = list(sorted(start_logs))
    assert len(start_logs) == 5
    last_elapsed = start_logs[0]
    for elapsed in start_logs[1:]:
        assert elapsed - last_elapsed >= 0.1
        last_elapsed = elapsed
    assert not redis.exists('redis_gt:test')


def test_throttle_works_with_para2(redis):

    def do_nothing():
        time.sleep(0.1)

    def do_nothing_with_throttle():
        throttle = Throttle('test', 2, redis)
        throttle.run(do_nothing)

    threads = [threading.Thread(target=do_nothing_with_throttle) for _ in range(5)]
    start_at = datetime.now().timestamp()
    await_threads(threads)
    elapsed = datetime.now().timestamp() - start_at
    assert 0.3 <= elapsed < 0.35
    assert not redis.exists('redis_gt:test')


def test_throttle_works_with_para5(redis):

    def do_nothing():
        time.sleep(0.1)

    def do_nothing_with_throttle():
        throttle = Throttle('test', 5, redis)
        throttle.run(do_nothing)

    threads = [threading.Thread(target=do_nothing_with_throttle) for _ in range(5)]
    start_at = datetime.now().timestamp()
    await_threads(threads)
    assert 0.1 <= datetime.now().timestamp() - start_at < 0.13
    assert not redis.exists('redis_gt:test')


def test_another_throttles_do_not_conflict(redis):

    def do_nothing():
        time.sleep(0.1)

    def do_nothing_with_throttle1():
        throttle = Throttle('test1', 2, redis)
        throttle.run(do_nothing)

    def do_nothing_with_throttle2():
        throttle = Throttle('test2', 2, redis)
        throttle.run(do_nothing)

    start_at = datetime.now().timestamp()
    await_threads([
        threading.Thread(target=do_nothing_with_throttle1),
        threading.Thread(target=do_nothing_with_throttle2),
    ])
    elapsed = datetime.now().timestamp() - start_at
    assert 0.1 <= elapsed < 0.13
    assert not redis.exists('redis_gt:test')


def test_throttle_raises_waiting_timeout_error_when_waiting_has_timeout(redis):
    errors = []

    def do_nothing():
        time.sleep(0.1)

    def do_nothing_with_throttle():
        nonlocal errors
        throttle = Throttle('test', 1, redis)
        try:
            throttle.run(do_nothing, waiting_timeout=0.05)
        except WaitingTimeoutError as wte:
            errors.append(wte)

    threads = [threading.Thread(target=do_nothing_with_throttle) for _ in range(5)]
    start_at = datetime.now().timestamp()
    await_threads(threads)
    assert 0.1 <= datetime.now().timestamp() - start_at < 0.13
    assert not redis.exists('redis_gt:test')


def test_throttle_removes_garbage_token(redis: StrictRedis):
    throttle = Throttle('test', 1, redis)

    def do_nothing():
        time.sleep(0.1)

    garbage_token = throttle.wait(1.0)
    assert redis.zscore('redis_gt:test', garbage_token)
    throttle.run(do_nothing)
    assert not redis.exists('redis_gt:test')
