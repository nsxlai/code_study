import sqlite3
import pandas as pd


class baseDB:
    def __init__(self):
        self.db_name = 'base'

    def all_data(self):
        self.display_db(f"SELECT * FROM {self.db_name}")

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


def query_01() -> None:
    ''' Query: Find the second highest salary '''
    t = employeeDB()
    t.insert_data(1, 100)
    t.insert_data(2, 200)
    t.insert_data(3, 500)
    t.insert_data(4, 400)
    print('-' * 30)
    t.all_data()

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
    p.all_data()

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
    w = weatherDB()
    w.insert_data(1, '2015-01-01', 10)
    w.insert_data(2, '2015-01-02', 25)
    w.insert_data(3, '2015-01-03', 20)
    w.insert_data(4, '2015-01-04', 30)
    print('-' * 30)
    w.all_data()

    print(' Solution '.center(30, '-'))
    sql_str = """SELECT DISTINCT a.Id
                 FROM Weather a, Weather b
                 WHERE a.Temperature > b.Temperature
                 AND DATEDIFF(a.Recorddate, b.Recorddate) = 1"""
    w.display_db(sql_str)


if __name__ == '__main__':
    query_01()
    query_02()
    # query_03()
