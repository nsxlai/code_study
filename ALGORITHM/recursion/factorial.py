from functools import lru_cache, reduce
from time import time


def fact(n):
    if n == 1:
        return 1
    else:
        return n*fact(n-1)


@lru_cache(maxsize=1000)  # LRU = Least Recently Used
def fact1(n):
    if n == 1:
        return 1
    else:
        return n * fact(n - 1)


def fact_mem(n):
    # Recursion with memorization
    if n in fact_cache:
        return fact_cache[n]

    if n == 1:
        value = 1
    else:
        value = n * fact_mem(n-1)

    fact_cache[n] = value
    return value


def fact_dp(n):
    # Dynamic programming, need to initialize a blank dictionary before calling this function.
    memo[0], memo[1] = 0, 1
    for i in range(2, n+1):
        memo[i] = i * memo[i-1]
        # print(f'{i=}; {memo[i]=}')
    return memo[n]


def iterative_factorial(n):  # iterative approach has the same structure as dynamic programming method
    f = 1
    for i in range(2, n+1):
        f *= i
    return f


if __name__ == '__main__':
    hi_value = 150

    print('-' * 45)
    t0 = time()
    print('Using recursive method without the lru_cache decorator')
    result = fact(hi_value)
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Recursive function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    t0 = time()
    print('Using recursive method with the lru_cache decorator (test run #1)')
    result = fact1(hi_value)
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Recursive function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    t0 = time()
    print('Using recursive method with the lru_cache decorator (test run #2)')
    result = fact1(hi_value)
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Recursive function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    print('Using lambda function method')
    t0 = time()
    result = reduce(lambda x, y: x*y, range(1, hi_value+1))
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Lambda function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    print('Using recursive with memorization method')
    t0 = time()
    fact_cache = {}  # Memorization method requires to initialize a blank dictionary before calling the function
    result = fact_mem(hi_value)
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Recursive with memorization function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    print('Using dynamic programming method')
    t0 = time()
    memo = {}  # Dynamic programming method requires to initialize a blank dictionary before calling the function
    result = fact_dp(hi_value)
    print(f'Factorial {hi_value}: {result:.4e}')
    t1 = time()
    print(f'Dynamic programming function runtime: {t1 - t0:.6f}\n')
