"""
source: https://medium.com/towards-data-science/understand-async-await-with-asyncio-for-asynchronous-programming-in-python-e0bc4d25808e

A CPU-bound task spends most of its time doing heavy calculations with the CPUs. If you are a data scientist and
need to train some machine learning models by crunching a huge amount of data, then it’s a CPU-bound task. If this
case, you should use multiprocessing to run your jobs in parallel and make full use of your CPUs.

On the other hand, an IO-bound task spends most of its time waiting for IO responses, which can be responses from
webpages, databases, or disks. For web development where a request needs to fetch data from APIs or databases,
it’s an IO-bound task and concurrency can be achieved with either threading or asyncio to minimize the waiting
time from external resources.
"""
import asyncio
from datetime import datetime


async def async_sleep(num):
    """
    Define coroutine with async def

    We can return a value in a coroutine function. The value is returned with the await command
    and can be assigned to a variable
    """
    print(f"Sleeping {num} seconds.")
    await asyncio.sleep(num)  # need to use the asyncio.sleep() in a coroutine function to simulate the IO blocking time


async def main():
    """
    Similarly, to run the code defined in a coroutine function, you need to await it. However, you cannot await
    it in the same way as you iterate a generator. A coroutine can only be awaited inside another coroutine
    defined by the async def syntax
    """
    start = datetime.now()

    coro_objs = []
    for i in range(1, 4):
        coro_objs.append(async_sleep(i))

    await asyncio.gather(*coro_objs)  # run multiple coroutines concurrently with the async.gather() function

    duration = datetime.now() - start
    print(f"Took {duration.total_seconds():.2f} seconds.")


if __name__ == '__main__':
    """
    For the top-level entry point coroutine function, which is normally named as main(), 
    we need to use asyncio.run() to run it
    """
    asyncio.run(main())
