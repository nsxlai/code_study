"""
source: https://towardsdatascience.com/5-common-sql-interview-problems-for-data-scientists-1bfa02d8bae6
    Weather DB schema:
        Id(INT), RecordDate(DATE), Temperature(INT)

    example:
    | Id(INT) | RecordDate(DATE) | Temperature(INT) |
    +---------+------------------+------------------+
    |       1 |       2015-01-01 |               10 |
    |       2 |       2015-01-02 |               25 |
    |       3 |       2015-01-03 |               20 |
    |       4 |       2015-01-04 |               30 |
"""
import sqlite3
import pandas as pd


class Weather:
    def __init__(self, wid, wdate, wtemp):
        self.wid = wid
        self.wdate = wdate
        self.wtemp = wtemp

    def __repr__(self):
        return f"Weather('{self.wid}, {self.wdate}, {self.wtemp}')"


class WeatherDB:
    """
        Basic SQL operation: CREATE, INSERT, SELECT, UPDATE, DELETE
        use the :memory" option to finetune the script before moving to the actual database file *.db
    """

    def __init__(self):
        """Once the DB file is created, will disable the file creation and chance to
           memory only
        """
        # self.conn = sqlite3.connect(':memory:')
        self.conn = sqlite3.connect('weather.db')
        self.c = self.conn.cursor()

    def create_table(self):
        self.c.execute("""CREATE TABLE weather (
                                          WeatherId integer,
                                          Date date,
                                          Temperature int)""")

    def insert_record(self, db):
        with self.conn:
            self.c.execute("INSERT INTO weather VALUES (:wid, :wdate, :wtemp)",
                           {'wid': db.wid, 'wdate': db.wdate, 'wtemp': db.wtemp})

    # def get_emps_by_name(self, emp):
    #     self.c.execute("SELECT * FROM employees WHERE first=:first AND last=:last", {'first': emp.first,
    #                                                                                  'last': emp.last})
    #     print(self.c.fetchall())
    #     return self.c.fetchall()

    def all_data(self):
        self.display_db("SELECT * FROM weather")
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

    def close_conn(self):
        self.conn.close()


if __name__ == '__main__':
    # Create the Department DB
    w1 = Weather(1, '2015-01-01', 50)
    w2 = Weather(2, '2015-01-02', 55)
    w3 = Weather(3, '2015-01-03', 60)
    w4 = Weather(4, '2015-01-04', 58)
    w5 = Weather(5, '2015-01-05', 55)
    w6 = Weather(6, '2015-01-06', 50)
    w7 = Weather(7, '2015-01-07', 53)
    w8 = Weather(8, '2015-01-08', 56)
    w9 = Weather(9, '2015-01-09', 60)
    w10 = Weather(10, '2015-01-10', 65)

    w_list = [w1, w2, w3, w4, w5, w6, w7, w8, w9, w10]

    w_record = WeatherDB()
    # w_record.create_table()  # Only need to creat the table once.
    for w in w_list:
        w_record.insert_record(w)

    w_record.all_data()
    w_record.close_conn()

