from unittest.mock import Mock
from datetime import datetime


tuesday = datetime(year=2019, month=1, day=1)
saturday = datetime(year=2019, month=1, day=5)

datetime = Mock()


def is_weekday():
    today = datetime.today()
    return 0 <= today.weekday() < 5


if __name__ == '__main__':
    datetime.today.return_value = tuesday
    assert is_weekday()

    datetime.today.return_value = saturday
    assert not is_weekday()
    # print(is_weekday())
    #
    # print(datetime.today().weekday())
    # print(datetime.today.return_value)
