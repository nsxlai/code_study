""" source from the SQL/02_sqlite/sql_demo.py """
import sqlite3
import pandas as pd
import os
from typing import List, Any, Tuple


class User:
    def __init__(self, id: int, username: str, password: str):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return f"User('{self.id}, {self.username}, {self.password}')"


class baseDB:
    def __init__(self):
        self.db_name = 'base'

    def all_data(self, table_name: str):
        self.display_db(f"SELECT * FROM {table_name}")

    def display_db(self, sql_str: str) -> Any:
        self.c.execute(sql_str)
        data = self.c.fetchall()
        col_desc = self.c.description
        if not col_desc:
            return "#### NO RESULTS ###"

        # columns = [col[0] for col in col_desc]
        # data = pd.DataFrame(data, columns=columns)
        # print(data)
        return data


class UserDB(baseDB):
    def __init__(self):
        """To initialize the database in memory only"""
        if os.path.isfile('users.db'):
            self.conn = sqlite3.connect('users.db')
        else:
            self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS users (id integer, username text, password text)")

    def insert_one(self, user: User) -> None:
        with self.conn:
            self.c.execute("INSERT INTO users VALUES (:id, :username, :password)",
                           {'id': user.id, 'username': user.username, 'password': user.password})

    def insert_many(self, user_list: List[Tuple[int, str, str]]) -> None:
        with self.conn:
            self.c.executemany("INSERT INTO users VALUES (?, ?, ?)", user_list)

    def all_users(self):
        self.c.execute("SELECT * FROM users")
        print(self.c.fetchall())
        return self.c.fetchall()

    def update_password(self, user: User, password: str):
        with self.conn:
            self.c.execute("""UPDATE users SET password = :password
                                WHERE username = :username""",
                           {'username': user.username, 'password': password})
        print(f'User {user.username} password is now updated')

    def remove_user(self, user: User):
        with self.conn:
            self.c.execute("DELETE from users WHERE username = :username",
                           {'username': user.username})

    def save_to_db(self):
        self.conn.commit()

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    """
    sqlite> select * from users;
    id          email_address           password
    ----------  --------------------    ----------
    1           john.doe@def.com        123456
    2           jane.doe@def.com        654321
    3           john.smith@def.com      abcabc
    4           mike.malloy@def.com     defdef
    5           aileen.chen@def.com     123123
    6           violet.minh@def.com     456456
    7           lucy.anderson@def.com   qwerty
    8           lisa.dinstill@def.com   aaabbb
    9           katie.sanero@def.com    cccddd
    10          sam.teller@def.com      efefef
    """
    user_list = [
        (1, 'john.doe@def.com', '123456'),
        (2, 'jane.doe@def.com', '654321'),
        (3, 'john.smith@def.com', 'abcabc'),
        (4, 'mike.malloy@def.com', 'defdef'),
        (5, 'aileen.chen@def.com', '123123'),
        (6, 'violet.minh@def.com', '456456'),
        (7, 'lucy.anderson@def.com', 'qwerty'),
        (8, 'lisa.dinstill@def.com', 'aaabbb'),
        (9, 'katie.sanero@def.com', 'cccddd'),
        (10, 'sam.teller@def.com', 'efefef'),
    ]

    users = UserDB()
    users.create_table()
    users.insert_many(user_list)

    # user1 = User(1, 'John', 'Doe', 80000)
    # user2 = User(2, 'Jane', 'Doe', 90000)
    # user3 = User(3, 'John', 'Smith', 85000)
    # user4 = User(4, 'Mike', 'Macey', 82000)
    # user5 = User(5, 'Aileen', 'Chen', 100000)

    print(users.display_db('select * from users'))

    # print('Update emp2 pay')
    # e.update_pay(emp2, 95000)
    # print(e.get_emps_by_name(emp2))
    #
    # print('Remove emp1 from the database')
    # e.remove_emp(emp1)
    # print(e.get_emps_by_name(emp1))
    #
    # print(e.get_emps_by_name(emp3))
    # print(e.all_emps())
    users.close_conn()
