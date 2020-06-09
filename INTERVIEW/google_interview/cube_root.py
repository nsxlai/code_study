"""
Without using Python standard library, create the function that does cube root of a number
"""
from time import time
from timeit import timeit


def ctimer(func):
    def wrapper(n):
        t0 = time()
        n_out = func(n)
        t1 = time()
        print(f'Function runtime is {t1 - t0}')
        return n_out
    return wrapper


@ctimer
def cube_root(n):
    i = 0.0
    while True:
        cube_i = i * i * i
        if cube_i < n:
            i += 0.0001
        elif cube_i == n:
            break
        else:
            i -= 0.0001
            break
    # print(f'cube root of {n} is {i:.4f}')
    return round(i, 4)


if __name__ == '__main__':
    print(f'n = 30; cube_root = {cube_root(30)}')
    print(f'n = 100; cube_root = {cube_root(100)}')
    print(f'n = 1000; cube_root = {cube_root(1000)}')
    print(f'n = 10000; cube_root = {cube_root(10000)}')
    print(f'n = 100000; cube_root = {cube_root(100000)}')