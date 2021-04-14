"""
source: https://betterprogramming.pub/6-alternatives-to-classes-in-python-6ecb7206377
"""
from math import sqrt
from typing import Optional
from dataclasses import dataclass


@dataclass
class Position:
    longitude: float
    latitude: float
    address: Optional[str] = None


def get_distance(p1: Position, p2: Position) -> float:
    horizontal = abs(p1.latitude - p2.latitude)
    vertical = abs(p1.longitude - p2.longitude)
    distance = sqrt(pow(horizontal, 2) + pow(vertical, 2))
    return distance


if __name__ == '__main__':
    pos1 = Position(49.0127913, 8.4231381, "Parkstraße 17")
    pos2 = Position(42.1238762, 9.1649964)
    print(get_distance(pos1, pos2))
