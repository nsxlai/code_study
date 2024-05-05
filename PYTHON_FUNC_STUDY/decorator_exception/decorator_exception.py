"""
This code has checks for 3 conditions:
1. If the value is in the sample_list, the value_screening function returns True
2. If the value is not in the sample_list and positive (>= 0), the value screening function returns False
3. If the value is negative, the value_screening function raise a CustomException

The decorator will have the enable arg set to either True or False. Toggle the enable to see the output
"""

from functools import wraps


class CustomException(Exception):
    pass


def cus_exception_guard(enable: bool):
    def input_func(func):
        @wraps(func)
        def inner(*arg):
            if enable:
                try:
                    return func(*arg)
                except CustomException as e:
                    print(e)
                    print('Encountered custom exception...')
            else:
                return func(*arg)
        return inner
    return input_func


@cus_exception_guard(enable=True)
def value_screening(val: int, lst: list) -> bool:
    """
    Check if the input value is not in the list
    """
    if val in lst:
        valid_value = True
    elif val not in lst and val >= 0:
        valid_value = False
    else:
        raise CustomException('The input key values is negative!!')

    return valid_value


if __name__ == '__main__':
    sample_list = [1, 3, 5, 7, 10, 14, 18, 21, 25]

    print(f'{value_screening(5, sample_list) = }')
    print(f'{value_screening(9, sample_list) = }')
    print(f'{value_screening(-3, sample_list) = }')
