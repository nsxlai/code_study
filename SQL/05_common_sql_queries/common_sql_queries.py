import sqlite3
import pandas as pd


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


class employeeDB(baseDB):
    def __init__(self):
        self.db_name = 'employee'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute(f"CREATE TABLE {self.db_name} (id integer, Salary integer)")

    def insert_data(self, pid, salary):
        with self.conn:
            self.c.execute(f"INSERT INTO {self.db_name} VALUES (:id, :salary)",
                           {'id': pid, 'salary': salary})


class personDB(baseDB):
    def __init__(self):
        self.db_name = 'person'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute(f"CREATE TABLE {self.db_name} (id integer, email text)")

    def insert_data(self, pid, email):
        with self.conn:
            self.c.execute(f"INSERT INTO {self.db_name} VALUES (:id, :email)",
                           {'id': pid, 'email': email})


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
        self.db_name = 'weather'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute(f"CREATE TABLE {self.db_name} (id integer, RecordDate date, temperature integer)")

    def insert_data(self, pid, rdate, temp):
        with self.conn:
            self.c.execute(f"INSERT INTO {self.db_name} VALUES (:id, :rdate, :temp)",
                           {'id': pid, 'rdate': rdate, 'temp': temp})


class new_employeeDB(baseDB):
    """
    The Employee table holds all employees. Every employee has an Id, a salary, and there is also a column for the department Id.
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
    def __init__(self):
        self.db_name = 'new_employee'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute(f"CREATE TABLE employee (id integer, name text, Salary integer, department_id integer)")
        self.c.execute(f"CREATE TABLE department (id integer, name text)")

    def insert_data(self, **kwargs):
        # print(f'{kwargs = }')
        table = kwargs.get('table')
        with self.conn:
            if table == 'employee':
                self.c.execute(f"INSERT INTO {table} VALUES (:id, :name, :salary, :department_id)",
                               {'id': kwargs['pid'], 'name': kwargs['name'], 'salary': kwargs['salary'],
                                'department_id': kwargs['did']})
            elif table == 'department':
                self.c.execute(f"INSERT INTO {table} VALUES (:id, :name)",
                               {'id': kwargs['pid'], 'name': kwargs['name']})


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
        self.db_name = 'student'
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute(f"CREATE TABLE {self.db_name} (id integer, name text)")

    def insert_data(self, pid, name):
        with self.conn:
            self.c.execute(f"INSERT INTO {self.db_name} VALUES (:id, :name)",
                           {'id': pid, 'name': name})


def query_01() -> None:
    ''' Query: Find the second highest salary '''
    print('\nQUERY #1')
    t = employeeDB()
    t.insert_data(1, 100)
    t.insert_data(2, 200)
    t.insert_data(3, 500)
    t.insert_data(4, 400)
    print('-' * 30)
    t.all_data('employee')

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
    p = personDB()
    p.insert_data(1, 'abc@test.com')
    p.insert_data(2, 'cde@test.com')
    p.insert_data(3, 'efg@test.com')
    p.insert_data(4, 'abc@test.com')
    p.insert_data(5, 'bcd@test.com')
    p.insert_data(6, 'efg@test.com')
    p.insert_data(7, 'bcd@test.com')
    p.insert_data(8, 'xyz@test.com')
    p.insert_data(9, 'bcd@test.com')
    print('-' * 30)
    p.all_data('person')

    print('-' * 30)
    print('SOLUTION 1: COUNT() in a Subquery')
    sql_str = """
              SELECT Email
              FROM (SELECT Email, count(Email) AS count
                    FROM Person
                    GROUP BY Email) as email_count
              WHERE count > 1"""
    p.display_db(sql_str)

    print('-' * 30)
    print('SOLUTION 2: HAVING Clause')
    sql_str = """SELECT email
                 FROM Person
                 GROUP BY Email
                 HAVING count(Email) > 1"""
    p.display_db(sql_str)


def query_03() -> None:
    ''' write a SQL query to find all dates Ids with higher temperature compared to its previous (yesterday's) dates.
        Sqlite3 does not support DATEDIFF function
    '''
    print('\nQUERY #3')
    w = weatherDB()
    w.insert_data(1, '2015-01-01', 10)
    w.insert_data(2, '2015-01-02', 25)
    w.insert_data(3, '2015-01-03', 20)
    w.insert_data(4, '2015-01-04', 30)
    print('-' * 30)
    w.all_data('weather')

    print(' Solution '.center(30, '-'))
    sql_str = """SELECT DISTINCT a.Id
                 FROM Weather a, Weather b
                 WHERE a.Temperature > b.Temperature
                 AND DATEDIFF(a.Recorddate, b.Recorddate) = 1"""
    w.display_db(sql_str)


def query_04() -> None:
    ''' Write a SQL query to find employees who have the highest salary in each of the departments '''
    print('\nQUERY #4')
    n = new_employeeDB()
    n.insert_data(table='employee', pid=1, name='Joe', salary=70000, did=1)
    n.insert_data(table='employee', pid=2, name='Jim', salary=90000, did=1)
    n.insert_data(table='employee', pid=3, name='Henry', salary=80000, did=2)
    n.insert_data(table='employee', pid=4, name='Sam', salary=60000, did=2)
    n.insert_data(table='employee', pid=5, name='Max', salary=90000, did=1)
    print('-' * 30)
    n.all_data('employee')
    n.insert_data(table='department', pid=1, name='IT')
    n.insert_data(table='department', pid=2, name='Sales')
    print('-' * 30)
    n.all_data('department')

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
    s.insert_data(1, 'Abbot')
    s.insert_data(2, 'Doris')
    s.insert_data(3, 'Emerson')
    s.insert_data(4, 'Green')
    s.insert_data(5, 'James')
    print('-' * 30)
    s.all_data('student')

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
    # query_03()
    query_04()
    query_05()
