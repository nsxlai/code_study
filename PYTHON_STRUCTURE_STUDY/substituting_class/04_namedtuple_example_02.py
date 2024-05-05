"""
source: https://betterprogramming.pub/6-alternatives-to-classes-in-python-6ecb7206377
"""
# Python 3.7 and later:
from typing import NamedTuple
from math import sqrt


class Position(NamedTuple):
    longitude: float
    latitude: float
    address: str = None


def get_distance(p1: Position, p2: Position) -> float:
    horizontal = abs(p1[0] - p2[0])
    vertical = abs(p1[1] - p2[1])
    distance = sqrt(pow(horizontal, 2) + pow(vertical, 2))
    return distance


if __name__ == '__main__':
    pos1 = Position(49.0127913, 8.4231381, "Parkstraße 17")
    pos2 = Position(42.1238762, 9.1649964)
    print(get_distance(pos1, pos2))
