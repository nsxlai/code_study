import sqlite3
import pandas as pd
from typing import Dict, List, Union, Any


class baseDB:
    def __init__(self):
        self.db_name = 'base'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.db_struct = {}

    def __create_table_str(self, table_name: str) -> str:
        """
        str out: CREATE TABLE employee (id integer, salary integer)
        """
        create_table_str = f"CREATE TABLE {table_name} ("
        for key, value in self.db_struct[table_name].items():
            temp_str = f'{key} {value}, '
            create_table_str += temp_str
        create_table_str = create_table_str[:-2] + ')'
        return create_table_str

    def __update_db_table_info(self, table_name: str, schema: Dict[str, str]):
        self.db_struct.setdefault(table_name, schema)

    def create_table(self, table_name: str, schema: Dict[str, str]) -> None:
        self.__update_db_table_info(table_name, schema)
        create_table_str = self.__create_table_str(table_name)
        with self.conn:
            # self.c.execute(f"CREATE TABLE {self.db_name} (id integer, Salary integer)")
            self.c.execute(create_table_str)

    def __insert_table_str(self, batch: bool, table_name: str) -> str:
        '''
        if batch is True:
            str output: INSERT INTO employee VALUES (:id, :salary)
        else:
            str output: INSERT INTO employee VALUES (?, ?)
        '''
        insert_table_str = f'INSERT INTO {table_name} VALUES ('
        keys = self.__find_schema_keys(table_name)
        for key in keys:
            if batch:
                temp_str = '?, '  # For batch importing, use ?
            else:
                temp_str = f':{key}, '
            insert_table_str += temp_str
        insert_table_str = insert_table_str[:-2] + ')'
        # print(f'{insert_table_str = }')
        return insert_table_str

    def __find_schema_keys(self, table_name: str) -> List[str]:
        return [i for i in self.db_struct[table_name]]

    def insert_one(self, table_name: str, *values: Union[Any]) -> None:
        insert_table_str = self.__insert_table_str(batch=False, table_name=table_name)
        keys = self.__find_schema_keys(table_name)
        with self.conn:
            self.c.execute(insert_table_str, {key: value for key, value in zip(keys, values)})

    def insert_batch(self, table_name: str, values: List[Union[Any]]) -> None:
        insert_table_str = self.__insert_table_str(batch=True, table_name=table_name)
        with self.conn:
            self.c.executemany(insert_table_str, values)

    def all_data(self, table_name: str) -> None:
        self.display_db(f"SELECT * FROM {table_name}")

    def display_db(self, sql_str: str) -> None:
        self.c.execute(sql_str)
        data = self.c.fetchall()
        col_desc = self.c.description
        if not col_desc:
            return "#### NO RESULTS ###"

        columns = [col[0] for col in col_desc]
        data = pd.DataFrame(data, columns=columns)
        print(data)


class employeeDB(baseDB):
    def __init__(self, dataset_sel: int):
        super().__init__()
        self.db_name = 'employee'
        if dataset_sel == 1:
            self._dataset_01()
        elif dataset_sel == 2:
            self._dataset_02()
        else:
            print(f'No dataset is selected')

    def _dataset_01(self):
        table_name = 'employee'
        schema = {'id': 'integer', 'salary': 'integer'}
        self.create_table(table_name=table_name, schema=schema)
        self.insert_one('employee', 1, 100)
        self.insert_one('employee', 2, 200)
        self.insert_one('employee', 3, 500)
        self.insert_one('employee', 4, 400)
        print('-' * 20)
        self.all_data(table_name)

    @classmethod
    def populate_dataset_01(cls):
        return cls(dataset_sel=1)

    def _dataset_02(self):
        """
        The Employee table holds all employees. Every employee has an Id, a salary, and department Id.
        +----+-------+--------+--------------+
        | Id | Name  | Salary | DepartmentId |
        +----+-------+--------+--------------+
        | 1  | Joe   | 70000  | 1            |
        | 2  | Jim   | 90000  | 1            |
        | 3  | Henry | 80000  | 2            |
        | 4  | Sam   | 60000  | 2            |
        | 5  | Max   | 90000  | 1            |
        +----+-------+--------+--------------+
        The Department table holds all departments of the company.
        +----+----------+
        | Id | Name     |
        +----+----------+
        | 1  | IT       |
        | 2  | Sales    |
        +----+----------+
        """
        table_name1 = 'employee'
        schema1 = {'id': 'integer', 'name': 'str', 'salary': 'integer', 'department_id': 'integer'}
        employee_data = [(1, 'Joe', 70000, 1),
                         (2, 'Jim', 90000, 1),
                         (3, 'Henry', 80000, 2),
                         (4, 'Sam', 60000, 2),
                         (5, 'Max', 90000, 1)]

        table_name2 = 'department'
        schema2 = {'id': 'integer', 'name': 'str'}
        department_data = [(1, 'IT'), (2, 'Sales')]

        self.create_table(table_name=table_name1, schema=schema1)
        self.insert_batch(table_name1, employee_data)
        print('-' * 30)
        self.all_data(table_name1)

        self.create_table(table_name=table_name2, schema=schema2)
        self.insert_batch(table_name2, department_data)
        print('-' * 30)
        self.all_data('department')

    @classmethod
    def populate_dataset_02(cls):
        return cls(dataset_sel=2)


if __name__ == '__main__':
    t1 = employeeDB.populate_dataset_01()

    print('\n' + ' Solution 1 '.center(30, '-'))
    sql_str = """SELECT DISTINCT Salary
               FROM employee
               ORDER BY Salary DESC
               LIMIT 1 OFFSET 1"""
    t1.display_db(sql_str)

    print('\n' + ' Solution 2 '.center(30, '-'))
    sql_str = """SELECT MAX(salary) AS SecondHighestSalary
               FROM employee
               WHERE salary != (SELECT MAX(salary) FROM employee)"""
    t1.display_db(sql_str)

    print()
    print(' dataset_02 '.center(40, '-'))
    t2 = employeeDB.populate_dataset_02()
