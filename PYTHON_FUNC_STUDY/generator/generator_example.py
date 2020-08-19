from itertools import cycle
from typing import Generator

colors = 'red orange yellow'.split()


def color_gen() -> Generator:
    for color in cycle(colors):
        # print(f'color = {color}')
        yield color


if __name__ == '__main__':
    c_gen = color_gen()
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))
