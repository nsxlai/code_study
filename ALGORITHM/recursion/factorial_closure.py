"""
source: https://www.youtube.com/watch?v=BiTsdi3uSzM&t=351s

RealPython Closure Course
"""


def _recurse_factorial(num):
    if num <= 1:
        return 1

    return num * _recurse_factorial(num - 1)


def first_factorial(num):
    if not isinstance(num, int):
        raise TypeError("Bad parameter; 'num' must be an integer")

    if num < 0:
        raise ValueError("Bad parameter; 'num must be >= 0")

    return _recurse_factorial(num)


def second_factorial(num):
    if not isinstance(num, int):
        raise TypeError("Bad parameter; 'num' must be an integer")

    if num < 0:
        raise ValueError("Bad parameter; 'num must be >= 0")

    def inner_factorial(num):
        ''' The inner_factorial function is "encapsulated" from the outer scope '''
        if num <= 1:
            return 1

        return num * inner_factorial(num - 1)

    return inner_factorial(num)


if __name__ == '__main__':
    print(f'{first_factorial(5) = }')
    print(f'{second_factorial(5) = }')
