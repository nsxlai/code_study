"""
source: https://betterprogramming.pub/6-alternatives-to-classes-in-python-6ecb7206377
"""
from typing import TypedDict, Optional
from math import sqrt


class Position(TypedDict):
    longitude: float
    latitude: float
    address: Optional[str]


def get_distance(p1: Position, p2: Position) -> float:
    horizontal = abs(p1.get("latitude") - p2.get("latitude"))
    vertical = abs(p1.get("longitude") - p2.get("longitude"))
    distance = sqrt(pow(horizontal, 2) + pow(vertical, 2))
    return distance


if __name__ == '__main__':
    pos1: Position = {"longitude": 49.0127913,
                      "latitude": 8.4231381,
                      "address": "Parkstraße 17"}
    pos2: Position = {"longitude": 42.1238762,
                      "latitude": 9.1649964,
                      "address": None}
    print(get_distance(pos1, pos2))
