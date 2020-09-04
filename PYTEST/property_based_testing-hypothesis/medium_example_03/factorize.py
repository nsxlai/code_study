from typing import List
import math


def factorize(number: int) -> List[int]:
    if number in [-1, 0, 1]:
        return [number]
    if number < 0:
        return [-1] + factorize(-number)
    factors = []

    # Treat the factor 2 on its own
    while number % 2 == 0:
        factors.append(2)
        number = number // 2
    if number == 1:
        return factors

    # Now we only need to check uneven numbers
    # up to the square root of the number
    i = 3
    while i <= int(math.ceil(number ** 0.5)) + 1:
        while number % i == 0:
            factors.append(i)
            number = number // i
        i += 2
    return factors


def factorize_rf(number: int) -> List[int]:
    if number in [-1, 0, 1]:
        return [number]
    if number < 0:
        return [-1] + factorize_rf(-number)
    factors = []

    # Treat the factor 2 on its own
    while number % 2 == 0:
        factors.append(2)
        number = number // 2
    if number == 1:
        return factors

    # Now we only need to check uneven numbers
    # up to the square root of the number
    i = 3
    # condition = int(math.ceil(number ** 0.5)) + 1
    while i <= number:  # fixed the issue prime number returns empty list
        while number % i == 0:
            factors.append(i)
            number = number // i
        i += 2
    return factors


if __name__ == '__main__':
    print(f'{factorize(2) = }')
    print(f'{factorize(4) = }')
    print(f'{factorize(5) = }')
    print(f'{factorize(12) = }')
    print(f'{factorize(27) = }')
    print('-' * 20)
    print(f'{factorize_rf(2) = }')
    print(f'{factorize_rf(4) = }')
    print(f'{factorize_rf(5) = }')
    print(f'{factorize_rf(12) = }')
    print(f'{factorize_rf(27) = }')
    print(f'{factorize_rf(100) = }')
