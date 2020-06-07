"""
source: https://towardsdatascience.com/5-common-sql-interview-problems-for-data-scientists-1bfa02d8bae6
    Department DB Schema:
        ID (INT), Name(Str)
"""
import sqlite3
import pandas as pd


class Department:
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Department('{self.id}, {self.name}')"


class DepartmentDB:
    """
        Basic SQL operation: CREATE, INSERT, SELECT, UPDATE, DELETE
        use the :memory" option to finetune the script before moving to the actual database file *.db
    """

    def __init__(self):
        """Once the DB file is created, will disable the file creation and chance to
           memory only
        """
        # self.conn = sqlite3.connect(':memory:')
        self.conn = sqlite3.connect('department.db')
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute("""CREATE TABLE departments (
                                          Id integer,
                                          Name text)""")

    def insert_record(self, db):
        with self.conn:
            self.c.execute("INSERT INTO departments VALUES (:id, :name)",
                           {'id': db.id, 'name': db.name})

    # def get_emps_by_name(self, emp):
    #     self.c.execute("SELECT * FROM employees WHERE first=:first AND last=:last", {'first': emp.first,
    #                                                                                  'last': emp.last})
    #     print(self.c.fetchall())
    #     return self.c.fetchall()

    def all_data(self):
        self.display_db("SELECT * FROM departments")
        return

    def display_db(self, sql_str):
        '''
        :param rowlens:
        :return:

        col_desc (cursor descript) has the format of:
        ('Id', None, None, None, None, None, None),
        ('FirstName', None, None, None, None, None, None),
        ...
        '''
        self.c.execute(sql_str)
        data = self.c.fetchall()
        col_desc = self.c.description
        if not col_desc:
            return "#### NO RESULTS ###"

        columns = [col[0] for col in col_desc]
        data = pd.DataFrame(data, columns=columns)
        print(data)
        return data

    def sql_execute(self, sql_str):
        self.c.execute(sql_str)
        data = self.c.fetchall()
        return data

    # def update_pay(self, emp, salary):
    #     with self.conn:
    #         self.c.execute("UPDATE employees SET pay = :salary
    #                          WHERE first = :first AND last = :last",
    #                        {'first': emp.first, 'last': emp.last, 'salary': salary})
    #     print(f'{emp.first} {emp.last} pay is now {salary}')
    #
    # def remove_emp(self, emp):
    #     with self.conn:
    #         self.c.execute("DELETE from employees WHERE first = :first AND last = :last",
    #                        {'first': emp.first, 'last': emp.last})

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    # Create the Department DB
    dep1 = Department(1, 'Engineering')
    dep2 = Department(2, 'IT')
    dep3 = Department(3, 'Marketing')
    dep4 = Department(4, 'Sales')

    dep_list = [dep1, dep2, dep3, dep4]

    # for emp in emp_list:
    #     print(f'{emp.first} {emp.last}: ID={emp.id}, '
    #           f'DepartmentId={emp.dpid}, Salary={emp.salary}')
    #     print(f'Email Address = {emp.email_id}')
    #     print('-' * 80)

    dep_record = DepartmentDB()
    for dep in dep_list:
        dep_record.insert_record(dep)

    print(dep_record.all_data())
    dep_record.close_conn()
