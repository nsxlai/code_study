import sqlite3
import pandas as pd
from typing import Dict, List, Union, Any


class baseDB:
    def __init__(self):
        self.db_name = 'base'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.db_struct = {}
        # self.schema_keys = [i for i in self.schema.keys()]
        # self.table_name = []

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
    def __init__(self):
        super().__init__()
        self.db_name = 'employee'

    def populate_dataset_01(self):
        table_name = 'employee'
        schema = {'id': 'integer', 'salary': 'integer'}
        self.create_table(table_name=table_name, schema=schema)
        self.insert_one('employee', 1, 100)
        self.insert_one('employee', 2, 200)
        self.insert_one('employee', 3, 500)
        self.insert_one('employee', 4, 400)
        print('-' * 30)
        self.all_data(table_name)

    def populate_dataset_02(self):
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


class emailDB(baseDB):
    def __init__(self):
        super().__init__()
        self.db_name = 'email'

    def populate_dataset_01(self):
        table_name = 'email'
        schema = {'id': 'integer', 'email_addr': 'str'}
        email_data = [(1, 'abc@test.com'),
                      (2, 'cde@test.com'),
                      (3, 'efg@test.com'),
                      (4, 'abc@test.com'),
                      (5, 'bcd@test.com'),
                      (6, 'efg@test.com'),
                      (7, 'bcd@test.com'),
                      (8, 'xyz@test.com'),
                      (9, 'bcd@test.com')]
        self.create_table(table_name=table_name, schema=schema)
        self.insert_batch(table_name, email_data)
        print('-' * 30)
        self.all_data(table_name)


class weatherDB(baseDB):
    """
    +---------+------------------+------------------+
    | Id(INT) | RecordDate(DATE) | Temperature(INT) |
    +---------+------------------+------------------+
    |       1 |       2015-01-01 |               10 |
    |       2 |       2015-01-02 |               25 |
    |       3 |       2015-01-03 |               20 |
    |       4 |       2015-01-04 |               30 |
    +---------+------------------+------------------+
    """

    def __init__(self):
        super().__init__()
        self.db_name = 'weather'

    def populate_dataset_01(self):
        table_name = 'weather'
        schema = {'id': 'integer', 'date': 'str', 'temperature': 'integer'}
        data = [(1, '2015-01-01', 10),
                (2, '2015-01-02', 25),
                (3, '2015-01-03', 20),
                (4, '2015-01-04', 30)]
        self.create_table(table_name=table_name, schema=schema)
        self.insert_batch(table_name, data)
        print('-' * 30)
        self.all_data(table_name)


class studentDB(baseDB):
    """
    +---------+---------+
    |    id   | student |
    +---------+---------+
    |    1    | Abbot   |
    |    2    | Doris   |
    |    3    | Emerson |
    |    4    | Green   |
    |    5    | James   |
    +---------+---------+
    """
    def __init__(self):
        super().__init__()
        self.db_name = 'student'

    def populate_dataset_01(self):
        table_name = 'student'
        schema = {'id': 'integer', 'name': 'str'}
        data = [(1, 'Abbot'), (2, 'Doris'), (3, 'Emerson'), (4, 'Green'), (5, 'James')]
        self.create_table(table_name=table_name, schema=schema)
        self.insert_batch(table_name, data)
        print('-' * 30)
        self.all_data(table_name)


def query_01() -> None:
    ''' Query: Find the second highest salary '''
    print('\nQUERY #1')
    t = employeeDB()
    t.populate_dataset_01()

    print('\n' + ' Solution 1 '.center(30, '-'))
    sql_str = """SELECT DISTINCT Salary
               FROM employee
               ORDER BY Salary DESC
               LIMIT 1 OFFSET 1"""
    t.display_db(sql_str)

    print('\n' + ' Solution 2 '.center(30, '-'))
    sql_str = """SELECT MAX(salary) AS SecondHighestSalary
               FROM employee
               WHERE salary != (SELECT MAX(salary) FROM employee)"""
    t.display_db(sql_str)


def query_02() -> None:
    ''' Write a SQL query to find all duplicate emails in a table '''
    print('\nQUERY #2')
    p = emailDB()
    p.populate_dataset_01()

    print('-' * 30)
    print('SOLUTION 1: COUNT() in a Subquery')
    sql_str = """
              SELECT email_addr
              FROM (SELECT email_addr, count(email_addr) AS count
                    FROM email
                    GROUP BY email_addr) as email_count
              WHERE count > 1"""
    p.display_db(sql_str)

    print('-' * 30)
    print('SOLUTION 2: HAVING Clause')
    sql_str = """SELECT email_addr
                 FROM email
                 GROUP BY email_addr
                 HAVING count(email_addr) > 1"""
    p.display_db(sql_str)


def query_03() -> None:
    ''' write a SQL query to find all dates Ids with higher temperature compared to its previous (yesterday's) dates.
        Sqlite3 does not support DATEDIFF function
    '''
    print('\nQUERY #3')
    w = weatherDB()
    w.populate_dataset_01()

    print('-' * 30)
    w.all_data('weather')

    print(' Solution '.center(30, '-'))
    sql_str = """SELECT DISTINCT a.Id
                 FROM Weather a, Weather b
                 WHERE a.Temperature > b.Temperature"""
                 # AND DATEDIFF(a.Recorddate, b.Recorddate) = 1"""
    w.display_db(sql_str)


def query_04() -> None:
    ''' Write a SQL query to find employees who have the highest salary in each of the departments '''
    print('\nQUERY #4')
    n = employeeDB()
    n.populate_dataset_02()

    print(' Solution '.center(30, '-'))
    sql_str = """SELECT Department.name AS 'Department', Employee.name AS 'Employee', Salary
                 FROM Employee
                 INNER JOIN Department ON Employee.Department_id = Department.Id
                 WHERE (Department_id , Salary) 
                 IN
                     (SELECT Department_id, MAX(Salary)
                      FROM Employee
                      GROUP BY Department_id)"""
    n.display_db(sql_str)


def query_05() -> None:
    """
    Write a query to change seats for the adjacent students
    """
    print('\nQUERY #5')
    s = studentDB()
    s.populate_dataset_01()

    print(' Solution '.center(30, '-'))
    sql_str = """SELECT 
                     CASE WHEN((SELECT MAX(id) FROM student)%2 = 1) AND id = (SELECT MAX(id) FROM student) THEN id
                          WHEN id%2 = 1 THEN id + 1
                     ELSE id - 1
                     END AS id, name
                 FROM student
                 ORDER BY id"""
    s.display_db(sql_str)


if __name__ == '__main__':
    query_01()
    query_02()
    query_03()
    query_04()
    query_05()
