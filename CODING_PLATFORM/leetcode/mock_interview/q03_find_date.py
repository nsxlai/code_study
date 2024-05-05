'''
Problem statement:
Given a list of timestamps in sequential order, return a list of lists grouped by week (7 days) using
the first timestamp as the starting point.

Example:

ts = [
    '2019-01-01',
    '2019-01-02',
    '2019-01-08',
    '2019-02-01',
    '2019-02-02',
    '2019-02-05',
]

output = [
    ['2019-01-01', '2019-01-02'],
    ['2019-01-08'],
    ['2019-02-01', '2019-02-02'],
    ['2019-02-05'],
]

import datetime

week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

if __name__ == '__main__':
    input_date = list(map(int, input("Enter date \n eg: 05/05/2019 \n\n").split('/')))
    print(input_date)
    day = datetime.date(input_date[2], input_date[0], input_date[1]).weekday()
    print(f'The input date is a {week_days[day]}')
'''
from datetime import datetime


def dayOfTheWeek(day: int, month: int, year: int) -> str:
    out = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    return out[datetime(year, month, day).weekday()]


if __name__ == '__main__':
    date_list = [(2020, 7, 28), (1991, 9, 14), (2010, 12, 25)]
    for year, month, day in date_list:
        print(f'Day of the week is {dayOfTheWeek(day, month, year)}')
