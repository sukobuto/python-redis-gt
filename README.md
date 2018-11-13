[![CircleCI](https://circleci.com/gh/sukobuto/py-recter.svg?style=svg&circle-token=cf630f735458471835e514b4fbfa917aa9970ff4)](https://circleci.com/gh/sukobuto/py-recter)

# Redis GT
Global throttling with Redis.

## usage

### throttling

```python
from recter import Throttle
import time
from threading import Thread
import redis

r = redis.from_url('redis://127.0.0.1:6379')

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
from recter import AsyncThrottle
import redis

async def do_something():
     await asyncio.sleep(1.0)

r = redis.from_url('redis://127.0.0.1:6379')

# max 10 parallels
throttle = AsyncThrottle(r, 'something', 10)

# 100 tasks of each 1sec.
tasks = [throttle.run(do_something()) for _ in range(100)]
loop = asyncio.get_event_loop()

# takes about 10secs (100tasks/10para).
loop.run_until_complete(asyncio.wait(tasks))
```

### decorator

```

```
