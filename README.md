[![PyPI pyversions](https://img.shields.io/pypi/pyversions/redis-gt.svg)](https://pypi.python.org/pypi/redis-gt/)
[![CircleCI](https://circleci.com/gh/sukobuto/python-redis-gt.svg?style=svg)](https://circleci.com/gh/sukobuto/python-redis-gt)

# Redis GT
Global throttling with Redis.

## installation

```
pip install redis-gt
```

## usage

ex) request with throttle

```python
import redis_gt
import requests

redis_gt.Defaults.redis_url = 'redis://127.0.0.1:6379'

def get_members(**kwargs):
    throttle = redis_gt.Throttle('backend_api_call', 20)
    return throttle.run(requests.get, '/api/members/', **kwargs)
```

ex) same with asyncio

```python
import asyncio
import redis_gt
import requests

redis_gt.Defaults.redis_url = 'redis://127.0.0.1:6379'

async def get_members(**kwargs):
    def _get():
        return requests.get('/api/members/', **kwargs)
    loop = asyncio.get_event_loop()
    throttle = redis_gt.AsyncThrottle('backend_api_call', 20)
    return await throttle.run(loop.run_in_executer(_get))
```

### throttling

```python
import redis_gt
import time
from threading import Thread

redis_gt.Defaults.redis_url = 'redis://127.0.0.1:6379'

def do_something():
    time.sleep(1.0)

def do_something_with_throttle():
    # max 10 parallels
    throttle = Throttle(r, 'something', 10)
    throttle.run(do_something)

# 100 tasks of each 1sec.
threads = [Thread(target=do_something_with_throttle) for _ in range(100)]
for t in threads:
    t.start()

# takes about 10secs (100tasks/10para).
for t in threads:
    t.join()
```

### throttling with asyncio

```python
import asyncio
from redis_gt import AsyncThrottle
import redis

async def do_something():
     await asyncio.sleep(1.0)

r = redis.StrictRedis.from_url('redis://127.0.0.1:6379')

# max 10 parallels
throttle = AsyncThrottle(r, 'something', 10)

# 100 tasks of each 1sec.
tasks = [throttle.run(do_something()) for _ in range(100)]
loop = asyncio.get_event_loop()

# takes about 10secs (100tasks/10para).
loop.run_until_complete(asyncio.wait(tasks))
```

### decorator

```python
from redis_gt import Throttle
from redis_gt.decorators import throttle
import redis

r = redis.StrictRedis.from_url('redis://127.0.0.1:6379')

# for sync function

@throttle('something', 10, redis=r)
def do_something():
    time.sleep(1.0)

# 100 tasks of each 1sec.
threads = [Thread(target=do_something) for _ in range(100)]
for t in threads:
    t.start()

# takes about 10secs (100tasks/10para).
for t in threads:
    t.join()

# for async function
@throttle('something', 10, redis=r)
async def do_something_async():
     await asyncio.sleep(1.0)

# 100 tasks of each 1sec.
tasks = [do_something_async() for _ in range(100)]
loop = asyncio.get_event_loop()

# takes about 10secs (100tasks/10para).
loop.run_until_complete(asyncio.wait(tasks))
```
