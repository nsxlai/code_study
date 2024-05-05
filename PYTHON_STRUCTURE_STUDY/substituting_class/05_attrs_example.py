"""
source: https://betterprogramming.pub/6-alternatives-to-classes-in-python-6ecb7206377
"""
from typing import Optional
import attr
from math import sqrt


@attr.s
class Position:
    longitude: float = attr.ib()
    latitude: float = attr.ib()
    address: Optional[str] = attr.ib(default=None)

    @longitude.validator
    def check_long(self, attribute, v):
        if not (-180 <= v <= 180):
            raise ValueError(f"Longitude was {v}, but must be in [-180, +180]")

    @latitude.validator
    def check_lat(self, attribute, v):
        if not (-90 <= v <= 90):
            raise ValueError(f"Latitude was {v}, but must be in [-90, +90]")


def get_distance(p1: Position, p2: Position) -> float:
    horizontal = abs(p1.latitude - p2.latitude)
    vertical = abs(p1.longitude - p2.longitude)
    distance = sqrt(pow(horizontal, 2) + pow(vertical, 2))
    return distance


if __name__ == '__main__':
    pos1 = Position(49.0127913, 8.4231381, "Parkstraße 17")
    pos2 = Position(42.1238762, 9.1649964)
    print(get_distance(pos1, pos2))
