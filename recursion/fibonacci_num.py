# Youtube video: https://www.youtube.com/watch?v=P8Xa2BitN3I&list=PLX6IKgS15Ue02WDPRCmYKuZicQHit9kFt&index=8
# Youtube video: https://www.youtube.com/watch?v=Qk0zUZW-U_M (for the fib_mem python example)
# Dynamic programming example: https://skerritt.blog/dynamic-programming/
# Given the follow example with fibonacci sequence, one is done recursively and one is done with memorization:
# The recursive has the time complexity of O(2^n). With memorization, the already calculated number will be
# stored and call statically
from functools import lru_cache
from time import time


# @lru_cache(maxsize=1000)  # LRU = Least Recently Used
def fib_recursive(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib_recursive(n-1) + fib_recursive(n-2)


def fib_recursive2(n):
    if n == 0 or n == 1:
        return n
    else:
        return fib_recursive2(n-1) + fib_recursive2(n-2)


def fib_mem(n):
    # Recursion with memorization
    if n in fib_cache:
        return fib_cache[n]

    if n <= 0:
        value = 0
    elif n == 1:
        value = 1
    else:
        value = fib_mem(n-1) + fib_mem(n-2)

    fib_cache[n] = value
    return value


def fib_dp(n):
    # Dynamic programming, need to initialize a blank dictionary before calling this function.
    memo[0], memo[1] = 0, 1
    for i in range(2, n+1):
        memo[i] = memo[i-2] + memo[i-1]
    return memo[n]


if __name__ == '__main__':
    hi_value = 35
    t0 = time()
    print('Using recursive method; try it with and without the lru_cache decorator')
    for i in range(hi_value):
        result = fib_recursive(i)
        # print(f'{i}: {result}')
    t1 = time()
    print(f'Recursive function runtime: {t1-t0}\n')

    print('Using recursive with memorization method')
    t0 = time()
    for i in range(hi_value):
        fib_cache = {}
        result = fib_mem(i)
        # print(f'{i}: {result}')
    t1 = time()
    print(f'Recursive with memorization function runtime: {t1-t0}\n')

    print('Using dynamic programming method')
    t0 = time()
    for i in range(hi_value):
        memo = {}
        result = fib_dp(i)
        # print(f'{i}: {result}')
    t1 = time()
    print(f'Dynamic programming function runtime: {t1 - t0}\n')
