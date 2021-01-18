# source: https://medium.com/better-programming/how-to-create-custom-classes-in-python-without-going-meta-5e8bfa97be6e
from __future__ import annotations
from type import
import os


class Warehouse:
    def run_query(self, query: str):
        pass

    def connect(self, username: str, password: str) -> Warehouse:
        raise NotImplementedError()


class BigQuery(Warehouse):
    def connect(self, username: str, password: str) -> BigQuery:
        print(f'BigQuery connect...')
        return self


class RedShift(Warehouse):
    def connect(self, username:str, password:str) -> RedShift:
        print(f'RedShift connect...')
        return self


class Snowflake(Warehouse):
    def connect(self, username:str, password:str) -> Snowflake:
        print(f'Snowflake connect...')
        return self


warehouses : Dict[str, Type[Warehouse]] = {
    "bigquery" : BigQuery,
    "redshift" : RedShift,
    "snowflake" : Snowflake
}

def get_connected_warehouse(warehouse:str) -> Warehouse:
    return warehouses.get(warehouse)().connect("medium", os.environ.get("PASSWORD"))
