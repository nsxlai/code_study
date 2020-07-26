from functools import wraps
from time import time, sleep


def run_time(func):
    '''Decorator function that calculate the function run time'''
    @wraps(func)
    def wrapper(*args):
        """wrapper function documentation"""
        t0 = time()
        data_out = func(*args)
        t1 = time()
        elapsed_time = t1 - t0
        print(f'Run time: {elapsed_time}')
        return data_out
    return wrapper


@run_time
def n_cubic(n):
    """n_cubic function documentation"""
    output = n * n * n
    sleep(1)
    return output


if __name__ == '__main__':
    print(f'n cubic output = {n_cubic(125)}')
    print(f'n_cubic.__name__ = {n_cubic.__name__}')
    print(f'n_cubic.__doc__  = {n_cubic.__doc__}')
    print()
    print('If the wraps decorator is disabled, the n_cubic.__name__ and __doc__ will both show')
    print('n_cubic.__name__ = wrapper')
    print('n_cubic.__doc__  = wrapper function documentation')
