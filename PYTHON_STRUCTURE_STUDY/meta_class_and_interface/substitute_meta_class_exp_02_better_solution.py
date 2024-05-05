"""
source: https://medium.com/better-programming/how-to-create-custom-classes-in-python-without-going-meta-5e8bfa97be6e

This solution certainly works, however, it has two drawbacks.
   1. When someone wants to add a new type of data warehouse, they have to know that it has to be added
      to the warehouses dictionary.
   2. When we provide this functionality by a library, extending this dictionary becomes even more cumbersome.
"""
from __future__ import annotations
from typing import Dict, Type, ClassVar
import os


class Warehouse:
    _registry: ClassVar[Dict[str, Type[Warehouse]]] = {}

    def __init_subclass__(cls, name: str, **kwargs):
        cls.name = name
        Warehouse._registry[name] = cls
        super().__init_subclass__(**kwargs)

    @classmethod
    def get(cls, name: str):
        return Warehouse._registry[name]

    def run_query(self, query: str):
        pass

    def connect(self, *args) -> Warehouse:
        raise NotImplementedError()


class BigQuery(Warehouse, name="bigquery"):
    def connect(self, username: str, password: str) -> BigQuery:
        print(f'BigQuery connect...')
        return self


class RedShift(Warehouse, name="redshift"):
    def connect(self, username: str, password: str) -> RedShift:
        print(f'RedShift connect...')
        return self


class Snowflake(Warehouse, name="snowflake"):
    def connect(self, username: str, password: str) -> Snowflake:
        print(f'Snowflake connect...')
        return self


def get_connected_warehouse(warehouse: str) -> Warehouse:
    return Warehouse.get(warehouse)().connect("medium", os.environ.get("PASSWORD"))


if __name__ == '__main__':
    get_connected_warehouse('snowflake')
    # w = Warehouse('BigQuery')
    # print(w._registry)
