from pprint import pprint
from typing import Dict


class user_data:
    def __init__(self, name: str, data: Dict[str, str]):
        self.name = name
        self.data = data


class data_base:
    _instance = None

    def __new__(self):
        if not self._instance:
            self._instance = super().__new__(self)
            self.db_core = {}
        return self._instance

    def create_user(self, name: str, data: Dict[str, str]):
        user = user_data(name, data)
        self.insert_data(user)

    def insert_data(self, user: user_data) -> None:
        self.db_core[user.name] = user.data

    def display(self) -> None:
        pprint(self.db_core)


if __name__ == '__main__':
    db = data_base()
    db.create_user(name='John', data={'Age': 35, 'Sex': 'M', 'Location': 'CA'})
    db.display()

    db.create_user(name='Mary', data={'Age': 20, 'Sex': 'F', 'Location': 'MA'})
    db.display()
