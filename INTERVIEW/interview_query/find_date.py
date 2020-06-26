'''
Problem statement:
Given a list of timestamps in sequential order, return a list of lists grouped by week (7 days) using the first timestamp as the starting point.

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
'''
import datetime

week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday','Sunday']

if __name__ == '__main__':
    input_date = list(map(int, input("Enter date \n eg: 05/05/2019 \n\n").split('/')))
    print(input_date)
    day = datetime.date(input_date[2], input_date[0], input_date[1]).weekday()
    print(f'The input date is a {week_days[day]}')
