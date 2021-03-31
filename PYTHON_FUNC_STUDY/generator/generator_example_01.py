from itertools import cycle
from typing import Generator

colors = 'red orange yellow'.split()


def color_gen() -> Generator:
    for color in cycle(colors):
        # print(f'color = {color}')
        yield color


def abc_gen() -> Generator:
    yield 'a'
    yield 'b'
    yield 'c'


if __name__ == '__main__':
    print('Display the generator object with "next()"')
    c_gen = color_gen()
    # print(c_gen)  # Printing the generator directly will not work. Can use the for loop to display the generator values
    # for color in c_gen:  # This will print the color in endless loop
    #     print(color)

    # To list each c_gen value, use the next() function
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))
    print(next(c_gen))

    print('-' * 20)
    print('Declare generator as an object for the loop')
    abc = abc_gen()
    for letter in abc:
        print(letter, end=' ')
    print()

    print('-' * 20)
    print('Directly pipe in the generator at the for loop')
    for letter in abc_gen():
        print(letter, end=' ')
    print()

    print('-' * 20)
    print('Create generator expression')
    gen = (x for x in range(10))  # create generator with output from 0 to 9
    for _ in gen:
        print(_, end=' ')
