"""
The "dayOfTheWeek" function is sourced from CODING_PLATFORM/leetcode/mock_interview/q03_find_date.py
"""
from datetime import datetime
import time


def dayOfTheWeek(day: int, month: int, year: int) -> str:
    out = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    return out[datetime(year, month, day).weekday()]


if __name__ == '__main__':
    # Example 1
    date_list = [(2020, 7, 28), (1991, 9, 14), (2010, 12, 25)]
    for year, month, day in date_list:
        print(f'Day of the week is {dayOfTheWeek(day, month, year)}')

    # Example 2
    current = datetime.now()
    date_format = f'{current.year}_{current.month}_{current.day}'
    time_format = f'{str(current.hour).zfill(2)}_{str(current.minute).zfill(2)}_{str(current.second).zfill(2)}'
    print(f'{date_format = }')
    print(f'{time_format = }')

    # Example 3
    print(f'Today is {current:%B} {current:%d}, {current:%Y}')  # capital %Y will display to full 4-digial year format
    print(f'Today is {current:%m}/{current:%d}/{current:%y}')  # lower case %y will just show 2-digital year format
    print(f'Current time is {current:%H}:{current:%M}:{current:%S}')

    # Example 4: use the time library to display time
    print(f'{time.time() = }')
    time.sleep(2)
    print(f'{time.time() = }')
