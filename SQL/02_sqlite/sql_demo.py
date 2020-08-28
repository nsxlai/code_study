import sqlite3
import pandas as pd
import os
from typing import List, Any, Tuple


class Employee:
    def __init__(self, pid, first, last, salary):
        self.pid = pid
        self.first = first
        self.last = last
        self.salary = salary

    @property
    def email(self):
        self.email_id = f'{self.first}.{self.last}@email.com'
        print(f'Email ID = {self.email_id}')
        return self.email_id

    @email.setter
    def email(self, email_id):
        self.email_id = email_id
        return f'Setting email to {email_id}'

    @property
    def fullname(self):
        return f'{self.first} {self.last}'

    def __repr__(self):
        return f"Employee('{self.first}, {self.last}, {self.pay}')"


class baseDB:
    def __init__(self):
        self.db_name = 'base'

    def all_data(self, table_name):
        self.display_db(f"SELECT * FROM {table_name}")

    def display_db(self, sql_str):
        self.c.execute(sql_str)
        data = self.c.fetchall()
        col_desc = self.c.description
        if not col_desc:
            return "#### NO RESULTS ###"

        columns = [col[0] for col in col_desc]
        data = pd.DataFrame(data, columns=columns)
        print(data)


class EmployeeDB(baseDB):
    def __init__(self):
        """To initialize the database in memory only"""
        if os.path.isfile('employee.db'):
            self.conn = sqlite3.connect('employee.db')
        else:
            self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute("CREATE TABLE IF NOT EXISTS employees (id integer, first text, last text, salary integer)")

    def insert_one(self, emp: Employee) -> None:
        with self.conn:
            self.c.execute("INSERT INTO employees VALUES (:id, :first, :last, :salary)",
                           {'id': emp.pid, 'first': emp.first, 'last': emp.last, 'salary': emp.salary})

    def insert_many(self, emp_list: List[Tuple[int, str, str, int]]) -> None:
        with self.conn:
            self.c.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", emp_list)

    def get_emps_by_name(self, emp):
        self.c.execute("SELECT * FROM employees WHERE first=:first AND last=:last", {'first': emp.first,
                                                                                     'last': emp.last})
        print(self.c.fetchall())
        return self.c.fetchall()

    def all_emps(self):
        self.c.execute("SELECT * FROM employees")
        print(self.c.fetchall())
        return self.c.fetchall()

    def update_pay(self, emp, salary):
        with self.conn:
            self.c.execute("""UPDATE employees SET salary = :salary
                                WHERE first = :first AND last = :last""",
                           {'first': emp.first, 'last': emp.last, 'salary': salary})
        print(f'{emp.first} {emp.last} pay is now {salary}')

    def remove_emp(self, emp):
        with self.conn:
            self.c.execute("DELETE from employees WHERE first = :first AND last = :last",
                           {'first': emp.first, 'last': emp.last})

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    """
    sqlite> select * from employees;
    id          first       last          salary
    ----------  ----------  ----------    ----------
    1           John        Doe            80000
    2           Jane        Doe            90000
    3           John        Smith          85000
    4           Mike        Malloy         82000
    5           Aileen      Chen           100000
    6           Violet      Minh           90000
    7           Lucy        Anderson       78000
    8           Lisa        Dinstill       80000
    9           Katie       Sanero         82000
    10          Sam         Teller         79000
    """
    employee_list = [
        (1, 'John', 'Doe', 80000),
        (2, 'Jane', 'Doe', 90000),
        (3, 'John', 'Smith', 85000),
        (4, 'Mike', 'Malloy', 82000),
        (5, 'Aileen', 'Chen', 100000),
        (6, 'Violet', 'Minh', 90000),
        (7, 'Lucy', 'Anderson', 78000),
        (8, 'Lisa', 'Dinstill', 80000), 
        (9, 'Katie', 'Sanero', 82000),
        (10, 'Sam', 'Teller', 79000),
    ]

    e = EmployeeDB()
    e.create_table()
    e.insert_many(employee_list)
    e.all_data('employees')

    emp1 = Employee(1, 'John', 'Doe', 80000)
    emp2 = Employee(2, 'Jane', 'Doe', 90000)
    emp3 = Employee(3, 'John', 'Smith', 85000)
    emp4 = Employee(4, 'Mike', 'Macey', 82000)
    emp5 = Employee(5, 'Aileen', 'Chen', 100000)

    '''
    emp_list = [emp1, emp2, emp3, emp4, emp5]

    for emp in emp_list:
        print(f'{emp.first} {emp.last} pay = {emp.pay}')
        emp.email
        print('-' * 45)

    emp_record = EmployeeDB()
    for emp in emp_list:
        emp_record.insert_emp(emp)
    '''
    print(e.display_db('select * from employees'))
    # query_name = e.get_emps_by_name(emp1)
    # print(query_name)

    print('Update emp2 pay')
    e.update_pay(emp2, 95000)
    print(e.get_emps_by_name(emp2))

    print('Remove emp1 from the database')
    e.remove_emp(emp1)
    print(e.get_emps_by_name(emp1))

    print(e.get_emps_by_name(emp3))
    print(e.all_emps())
    e.close_conn()
