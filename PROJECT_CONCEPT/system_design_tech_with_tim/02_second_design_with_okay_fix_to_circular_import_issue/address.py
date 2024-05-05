"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial

The original code use simple class structure; updated to dataclass structure
"""
from dataclasses import dataclass


@dataclass()
class Address:
    country: str
    state: str
    city: str
    street: str
    postal_code: str
