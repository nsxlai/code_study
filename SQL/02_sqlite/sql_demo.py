import sqlite3


class Employee:
    def __init__(self, first, last, pay):
        self.first = first
        self.last = last
        self.pay = pay

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
        Basic SQL operation: INSERT, SELECT, UPDATE, DELETE
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
        """To initialize the database in memory only"""
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE employees (
                                          first text,
                                          last text,
                                          pay integer
                                          )""")

    def insert_emp(self, emp):
        with self.conn:
            self.c.execute("INSERT INTO employees VALUES (:first, :last, :pay)", {'first': emp.first,
                                                                             'last': emp.last,
                                                                             'pay': emp.pay})

    def get_emps_by_name(self, emp):
        self.c.execute("SELECT * FROM employees WHERE first=:first AND last=:last", {'first': emp.first,
                                                                                     'last': emp.last})
        print(self.c.fetchall())
        return self.c.fetchall()

    def all_emps(self):
        self.c.execute("SELECT * FROM employees")
        print(self.c.fetchall())
        return self.c.fetchall()

    def update_pay(self, emp, pay):
        with self.conn:
            self.c.execute("""UPDATE employees SET pay = :pay
                             WHERE first = :first AND last = :last""",
                           {'first': emp.first, 'last': emp.last, 'pay': pay})
        print(f'{emp.first} {emp.last} pay is now {pay}')

    def remove_emp(self, emp):
        with self.conn:
            self.c.execute("DELETE from employees WHERE first = :first AND last = :last",
                           {'first': emp.first, 'last': emp.last})

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    emp1 = Employee('John', 'Doe', 80000)
    emp2 = Employee('Jane', 'Doe', 90000)
    emp3 = Employee('John', 'Smith', 85000)
    emp4 = Employee('Mike', 'Macey', 82000)
    emp5 = Employee('Aileen', 'Chen', 100000)
    emp_list = [emp1, emp2, emp3, emp4, emp5]

    for emp in emp_list:
        print(f'{emp.first} {emp.last} pay = {emp.pay}')
        emp.email
        print('-' * 45)

    emp_record = EmployeeDB()
    for emp in emp_list:
        emp_record.insert_emp(emp)

    print(emp_record.all_emps())
    query_name = emp_record.get_emps_by_name(emp1)
    print(query_name)

    print('Update emp2 pay')
    emp_record.update_pay(emp2, 95000)
    print(emp_record.get_emps_by_name(emp2))

    print('Remove emp1 from the database')
    emp_record.remove_emp(emp1)
    print(emp_record.get_emps_by_name(emp1))

    print(emp_record.get_emps_by_name(emp3))
    print(emp_record.all_emps())
    emp_record.close_conn()
