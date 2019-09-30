"""
Without using Python standard library, create the function that does cube root of a number
"""
from time import time


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
            i = i + 0.1
        else:
            i = i - 0.1
            break
    return '{0:.4f}'.format(i)


if __name__ == '__main__':
    print(f'n = 30; cube_rooot = {cube_root(30)}')
    print(f'n = 100; cube_rooot = {cube_root(100)}')
    print(f'n = 1000; cube_rooot = {cube_root(1000)}')
    print(f'n = 10000; cube_rooot = {cube_root(10000)}')
