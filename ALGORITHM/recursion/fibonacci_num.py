# Youtube video: https://www.youtube.com/watch?v=P8Xa2BitN3I&list=PLX6IKgS15Ue02WDPRCmYKuZicQHit9kFt&index=8
# Youtube video: https://www.youtube.com/watch?v=Qk0zUZW-U_M (for the fib_mem python example)
# Dynamic programming example: https://skerritt.blog/dynamic-programming/
# Given the follow example with fibonacci sequence, one is done recursively and one is done with memorization:
# The recursive has the time complexity of O(2^n). With memorization, the already calculated number will be
# stored and call statically
from functools import lru_cache
from time import time


def measure_elapsed_time(func):
    def wrapper(n):
        t0 = time()
        result = func(n)
        # print(f'Fibanacci {n}: {result}')
        t1 = time()
        print(f'Recursive function runtime: {t1-t0:.6f}\n')
        return result
    return wrapper


def fib_recursive(n):
    if n == 0 or n == 1:
        return n
    else:
        return fib_recursive(n-1) + fib_recursive(n-2)


@lru_cache(maxsize=1000)  # LRU = Least Recently Used
def fib_recursive1(n):
    if n == 0 or n == 1:
        return n
    else:
        return fib_recursive(n-1) + fib_recursive(n-2)


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
        # print(f'{i=}; {memo[i]=}')
    return memo[n]


def fib_iter(n):
    if not isinstance(n, int):
        raise TypeError('Fibonacci number is integer only')
    if n < 0:
        raise ValueError('Fibonacci number is positive')
    if n == 1:
        return 1
    a, b = 1, 2
    for _ in range(n-3):  # range start with 0. Need to subtract the first 3 elements off (0, 1, and 2) for the loop
        a, b = b, a+b
    # print(f'{_=}, {b=}')
    return b


if __name__ == '__main__':
    """
    Using decorator to measure the time performance for each of the method does not work well with recursive algorithm.
    Only the dynamic programming method can work with timer decorator since it does not have recursive loop.
    
    Summary:
    Method 1: recursive method without the lru_cache decorator
       => The function will run about 16.192276 seconds
    Method 2: recursive method with the lru_cache decorator
       => The function will run about 15.956877 seconds. There isn't a lot of performance gain
    Method 3: Use lambda function. It is slightly faster than method 1 and 2
    Method 4: recursive method with the lru_cache decorator (same test run as method 2)
       => The lru cache is used to provide the previously calculated data and boosted the performance to only access
          time to get the data directly without any calculation. The run time is around 0.000007 second
    Method 5: Using recursive with memorization method
       => The Memorization method significantly reduce the amount of repeated calculation via recursive loops. The run
          time is around 0.000033 seconds
    Method 6: Using dynamic programming method instead of recursive loops. 
       => This method will calculate the value from the first element until the last, which is the opposite of the
          recursive looping methodology (calculate backward from the last element. The run time very fast and takes
          about 0.000014 seconds (second fastest after the second run of LRU cached method).       
    """
    hi_value = 36

    print('-' * 45)
    t0 = time()
    print('Using recursive method without the lru_cache decorator')
    result = fib_recursive(hi_value)
    print(f'Fibonacci {hi_value}: {result}')
    t1 = time()
    print(f'Recursive function runtime: {t1-t0:.6f}\n')

    print('-' * 45)
    t0 = time()
    print('Using recursive method with the lru_cache decorator (test run #1)')
    result = fib_recursive1(hi_value)
    print(f'Fibonacci {hi_value}: {result}')
    t1 = time()
    print(f'Recursive function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    t0 = time()
    print('Using recursive method with the lru_cache decorator (test run #2)')
    result = fib_recursive1(hi_value)
    print(f'Fibonacci {hi_value}: {result}')
    t1 = time()
    print(f'Recursive function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    print('Using lambda function method')
    t0 = time()
    fib = lambda x: x if x <= 1 else fib(x - 1) + fib(x - 2)
    print(f'Fibonacci {hi_value}: {fib(hi_value)}')
    t1 = time()
    print(f'Lambda function runtime: {t1 - t0:.6f}\n')

    print('-' * 45)
    print('Using recursive with memorization method')
    t0 = time()
    fib_cache = {}  # Memorization method requires to initialize a blank dictionary before calling the function
    result = fib_mem(hi_value)
    print(f'Fibonacci {hi_value}: {result}')
    t1 = time()
    print(f'Recursive with memorization function runtime: {t1-t0:.6f}\n')

    print('-' * 45)
    print('Using dynamic programming method')
    t0 = time()
    memo = {}  # Dynamic programming method requires to initialize a blank dictionary before calling the function
    result = fib_dp(hi_value)
    print(f'Fibonacci {hi_value}: {result}')
    t1 = time()
    print(f'Dynamic programming function runtime: {t1-t0:.6f}\n')

    print('-' * 45)
    print('Using iterative programming method. This method is extremely fast...')
    t0 = time()
    result = fib_iter(150)
    print(f'Fibonacci {150}: {result}')
    t1 = time()
    print(f'Iterative programming function runtime: {t1 - t0:.6f}\n')
