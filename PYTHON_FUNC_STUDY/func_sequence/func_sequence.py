"""
This code derived from the state.py design pattern

In a finite state machine, defining a sequence to delivery the state payload
will be the key to step through the state machine.
"""


def a():
    return 'running func a'


def b():
    return 'running func b'


def c():
    return 'running func c'


if __name__ == '__main__':
    # Run function a 3 times, function b 1 time, and function c 2 times
    sequence = [a] * 3 + [b] + [c] * 2
    print(f'{sequence = }')
    for func in sequence:
        print(func)
        print(func())

    # Can also use generator
    print('-' * 30)
    sequence_gen = ([a] * 3 + [b] + [c] * 2) * 2  # run the sequence twice
    print(f'{sequence_gen = }')
    for func in sequence_gen:
        print(func())
