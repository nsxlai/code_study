"""
source: https://betterprogramming.pub/understand-python-decorators-in-3-minutes-ec48fdc8e2cf
"""
from typing import Callable
from functools import wraps
from time import sleep


def guard_zero(enable: bool):
    def func_input(operate: Callable):
        @wraps(operate)
        def inner(x, y):
            """ Decorator that checks the Y value (cannot be 0) """
            if enable and y == 0:
                print("Cannot divide by 0.")
                return
            return int(operate(x, y)) # if enable else operate(x, y)
        return inner
    return func_input


@guard_zero(enable=True)
def divide1(x, y):
    """
    This divide function has the GuardZero enabled
    """
    return x / y


@guard_zero(enable=False)
def divide2(x, y):
    """
    This divide function has the GuardZero disabled
    """
    return x / y


if __name__ == '__main__':
    print(f'divide1.__name__ = {divide1.__name__}')
    print(f'divide1.__doc__  = {divide1.__doc__}')
    print(f'{divide1(10, 5) = }')
    print(f'{divide1(5, 0) = }')

    print(f'divide2.__name__ = {divide2.__name__}')
    print(f'divide2.__doc__  = {divide2.__doc__}')
    print(f'{divide2(10, 5) = }')
    sleep(1)
    print(f'{divide2(5, 0) = }')
