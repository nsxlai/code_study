"""
source: https://betterprogramming.pub/understand-python-decorators-in-3-minutes-ec48fdc8e2cf
"""
from typing import Callable
from functools import wraps


def guard_zero(out_type: bool):
    def func_input(operate: Callable):
        @wraps(operate)
        def inner(x, y):
            """ Decorator that checks the Y value (cannot be 0) """
            if y == 0:
                print("Cannot divide by 0.")
                return
            return int(operate(x, y)) if out_type else operate(x, y)
        return inner
    return func_input


@guard_zero(out_type=True)
def divide1(x, y):
    return x / y


@guard_zero(out_type=False)
def divide2(x, y):
    return x / y


if __name__ == '__main__':
    print(f'{divide1(10, 5) = }')
    print(f'{divide2(10, 5) = }')
    print(f'divide1.__name__ = {divide1.__name__}')
    print(f'divide1.__doc__  = {divide1.__doc__}')
