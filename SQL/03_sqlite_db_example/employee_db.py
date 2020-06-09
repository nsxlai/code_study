"""
source: https://towardsdatascience.com/5-common-sql-interview-problems-for-data-scientists-1bfa02d8bae6
    Employee DB schema:
        ID (INT), FirstName(Str), LastName(Str), EmailAddr(Str), DepartmentID(INT), Salary(INT),
"""
import sqlite3
import pandas as pd


class Employee:
    def __init__(self, id, first, last, dpid, salary):
        self.id = id
        self.first = first
        self.last = last
        self.dpid = dpid
        self.salary = salary
        self.email_id = f'{first.lower()}.{last.lower()}@email.com'

    @property
    def email(self):
        print(self.email_id)
        return self.email_id

    @email.setter
    def email(self, email_id):
        self.email_id = email_id
        print(f'Setting email to {self.email_id}')

    @property
    def fullname(self):
        return f'{self.first} {self.last}'

    def __repr__(self):
        return f"Employee('{self.id}, {self.first}, {self.last}, {self.dpid}, {self.salary}')"


class Borg:
    """Borg pattern making the class attributes global"""
    _shared_data = {}  # Attribute dictionary

    def __init__(self):
        self.__dict__ = self._shared_data  # Make it an attribute dictionary


class Singleton(Borg):  # Inherits from the Borg class
    """This class now shares all its attributes among its various instances"""

    # This essenstially makes the singleton objects an object-oriented global variable

    def __init__(self, **kwargs):
        Borg.__init__(self)
        self._shared_data.update(kwargs)  # Update the attribute dictionary by inserting a new key-value pair

    def __str__(self):
        return str(self._shared_data)  # Returns the attribute dictionary for printing


class OneOnly:
    _singleton = None
    def __new__(cls, *args, **kwargs):
        if not cls._singleton:
            # THEN
            cls._singleton = super(OneOnly, cls).__new__(cls, *args, **kwargs)
            # ENDIF;
        return cls._singleton


class EmployeeDB:
    """
        Basic SQL operation: CREATE, INSERT, SELECT, UPDATE, DELETE
        use the :memory" option to finetune the script before moving to the actual database file *.db
    """
    # def __init__(self, first, last, pay):
    #     self.first = first
    #     self.last = last
    #     self.pay = pay
    #
    # _singleton_db = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls._singleton_db
    #         cls._singleton_db = super(EmployeeDB, cls.__new__(cls, *args, **kwargs))
    #     return cls._singleton_db
    # conn = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if not cls.conn:
    #         cls.conn = sqlite3.connect('employee.db')
    #     cls.c = cls.conn.cursor()
    #     cls.c.execute("""CREATE TABLE employees (
    #                                   first text,
    #                                   last text,
    #                                   pay integer
    #                                   )""")

    def __init__(self):
        """Once the DB file is created, will disable the file creation and chance to
           memory only
        """
        # self.conn = sqlite3.connect(':memory:')
        self.conn = sqlite3.connect('employee.db')
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute("""CREATE TABLE employees (
                                          Id integer,
                                          FirstName text,
                                          LastName text,
                                          EmailAddr text,
                                          DepartmentId integer,
                                          Salary integer
                                          )""")

    def insert_emp(self, emp):
        with self.conn:
            self.c.execute("INSERT INTO employees VALUES (:id, :first, :last, :email, :dpid, :salary)",
                           {'id': emp.id, 'first': emp.first, 'last': emp.last, 'email': emp.email,
                            'dpid': emp.dpid, 'salary': emp.salary})

    def get_emps_by_name(self, emp):
        self.c.execute("SELECT * FROM employees WHERE first=:first AND last=:last", {'first': emp.first,
                                                                                     'last': emp.last})
        print(self.c.fetchall())
        return self.c.fetchall()

    def all_data(self):
        self.display_db("SELECT * FROM employees")
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

    def update_pay(self, emp, salary):
        with self.conn:
            self.c.execute("""UPDATE employees SET salary = :salary
                             WHERE first = :first AND last = :last""",
                           {'first': emp.first, 'last': emp.last, 'salary': emp.salary})
        print(f'{emp.first} {emp.last} pay is now {salary}')

    def remove_emp(self, emp):
        with self.conn:
            self.c.execute("DELETE from employees WHERE first = :first AND last = :last",
                           {'first': emp.first, 'last': emp.last})

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    # Create the Employee DB
    emp1 = Employee(1, 'John', 'Doe', 1, 80000)
    emp2 = Employee(2, 'Jane', 'Doe', 2, 90000)
    emp3 = Employee(3, 'John', 'Smith', 1, 85000)
    emp4 = Employee(4, 'Mike', 'Macey', 3, 82000)
    emp5 = Employee(5, 'Aileen', 'Chen', 2, 100000)
    emp6 = Employee(6, 'Violet', 'Minh', 1, 75000)
    emp7 = Employee(7, 'Lucy', 'Merry', 4, 90000)
    emp8 = Employee(8, 'Lisa', 'Dinstill', 4, 80000)
    emp9 = Employee(9, 'Katie', 'Sandy', 1, 82000)
    emp10 = Employee(10, 'Sam', 'Teller', 2, 79000)
    emp_list = [emp1, emp2, emp3, emp4, emp5, emp6, emp7, emp8, emp9, emp10]

    emp_record = EmployeeDB()
    for emp in emp_list:
        emp_record.insert_emp(emp)

    print(emp_record.all_data())
    emp_record.close_conn()
