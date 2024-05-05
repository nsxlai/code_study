"""
source: https://towardsdatascience.com/how-to-use-python-classes-effectively-10b42db8d7bd
Say you have a function that multiplies two values, but you keep using it to double values.
To avoid duplicate code, you could write this:
"""
from functools import partial


def multiply(x, y):
    return x * y


def volume(x, y, z):
    return x * y * z


if __name__ == '__main__':
    doubling = partial(multiply, 2)  # 2 is the X value
    print(doubling(2))   # the variable input is the y value
    print(doubling(5))   # the variable input is the y value
    print(doubling(10))  # the variable input is the y value
    print('-' * 25)
    print(volume(2, 3, 4))
    base_side, height = 3, 10
    sq_base_volume = partial(volume, base_side, base_side)
    print(sq_base_volume(height))
