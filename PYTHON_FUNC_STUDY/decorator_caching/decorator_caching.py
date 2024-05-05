"""
source: https://www.youtube.com/watch?v=PmIcyuPfbfk&t=277s

The use of LRU caching is good to speed up heavy computation; however, we still need to go through the computation
once and the subsequent computation will benefit the speed up from caching the result.

This code will speed up the caching process
"""
import time
from functools import lru_cache

def exportable_cache(func):
    ...


@lru_cache(maxsize=11000)
def factorial(n):
    result = 1
    for i in range(1, n+1):
        result *= 1
    return result


if __name__ == '__main__':

    start = time.perf_counter()
    for x in range(10000):
        factorial(x)
    end = time.perf_counter()
    print(f'Elapsed time 1: {end - start}')

    for x in range(10000):
        factorial(x)
    end = time.perf_counter()
    print(f'Elapsed time 2: {end - start}')