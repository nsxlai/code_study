"""
source: https://towardsdatascience.com/5-common-sql-interview-problems-for-data-scientists-1bfa02d8bae6
    Employee DB schema:
        ID (INT), FirstName(Str), LastName(Str), EmailAddr(Str), DepartmentID(INT), Salary(INT),

    Department DB Schema:
        ID (INT), Name(Str)

    Weather DB schema:
        Id(INT), RecordDate(DATE), Temperature(INT)
"""
import sqlite3
from employee_db import EmployeeDB
from department_db import DepartmentDB
from weather_db import WeatherDB


class Adapter:
    """This changes the generic method name to individualized method names"""

    def __init__(self, object, **adapted_method):
        """Change the name of the method"""
        self._object = object
        self.__dict__.update(adapted_method)

    def __getattr__(self, attr):
        """Simply return the rest of attributes!"""
        return getattr(self._object, attr)


if __name__ == '__main__':
    db = []
    emp_record = EmployeeDB()
    # emp_record.all_data()
    # print('-' * 80)
    dep_record = DepartmentDB()
    # dep_record.all_data()
    w_record = WeatherDB()

    # Adapter pattern
    db.append(Adapter(emp_record, disp=emp_record.all_data))
    db.append(Adapter(dep_record, disp=dep_record.all_data))
    db.append(Adapter(w_record, disp=w_record.all_data))
    print(f'db = {db}')
    for _ in db:
        print(_.disp())

    while True:
        sql_str = input('Enter the SQL cmd: \n')
        if sql_str == 'quit':
            break
        try:
            if 'employees' in sql_str:
                query_result = emp_record.display_db(sql_str)
            elif 'department' in sql_str:
                query_result = dep_record.display_db(sql_str)
            elif 'weather' in sql_str:
                query_result = w_record.display_db(sql_str)
        except sqlite3.OperationalError:
            print('Bad query... Try again')
        continue
    # query_name = emp_record.get_emps_by_name(emp1)
    # print(query_name)
    #
    # print('Update emp2 pay')
    # emp_record.update_pay(emp2, 95000)
    # print(emp_record.get_emps_by_name(emp2))
    #
    # print('Remove emp1 from the database')
    # emp_record.remove_emp(emp1)
    # print(emp_record.get_emps_by_name(emp1))
    #
    # print(emp_record.get_emps_by_name(emp3))
    # print(emp_record.all_emps())
    emp_record.close_conn()
