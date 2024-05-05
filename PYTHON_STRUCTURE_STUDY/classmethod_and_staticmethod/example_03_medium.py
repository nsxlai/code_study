"""
source: https://towardsdatascience.com/build-factory-and-utility-in-your-python-classes-ea39e267ca0a
"""
import re
from datetime import datetime


class Employee:
    def __init__(self, name, year_joined):
        self.name = name
        self.year_joined = year_joined

    @classmethod
    def from_string(cls, string):
        name = re.search('I am (.*?) ', string).group(1)
        year_joined = int(re.search('joined in (\d+).', string).group(1))
        return cls(name, year_joined)

    @staticmethod
    def calc_year(year_joined, year_now):
        length = year_now - year_joined
        if length > 0:
            return f'{length} years'
        else:
            return 'less than one year'

    def seniority(self):
        n_years = self.calc_year(self.year_joined, datetime.now().year)
        print(f'{self.name} has worked in our company for {n_years}')

    @property
    def year_joined(self):
        print('getting year_joined...')
        return self._year_joined

    @year_joined.setter
    def year_joined(self, value):
        print('setting year_joined...')
        self._year_joined = value

    @year_joined.deleter
    def year_joined(self):
        print('deleting year_joined...')
        del self._year_joined


if __name__ == '__main__':
    e1 = Employee.from_string('I am Chris and I joined in 2020.')
    e1.seniority()

    print(Employee.calc_year(2021, 2009))

    print('-' * 25)
    e2 = Employee('Chris', 2020)
    print(f'{e2.year_joined = }')
    e2.year_joined = 2021
    print(f'{e2.year_joined = }')
    print(f'{e2.__dict__ = }')
    del e2.year_joined
    print(f'{e2.__dict__ = }')
