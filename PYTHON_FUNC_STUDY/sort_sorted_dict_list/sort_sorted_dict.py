"""
source: https://www.geeksforgeeks.org/python-sort-dictionary-by-value-difference/
"""

MAIN_DICT = {'gfg': [34, 87],
             'is': [10, 13],
             'best': [19, 27],
             'for': [10, 50],
             'geeks': [15, 45]}

SCORE = {20: 60,
         100: 50.0,
         41: 20.5,
         67: 33.5,
         23: 69,
         15: 45,
         72: 36.0,
         10: 30,
         97: 48.5,
         55: 27.5,
         84: 42.0,
         32: 96,
         90: 45.0,
         27: 81,
         47: 23.5,
         25: 75,
         45: 22.5,
         40: 20.0,
         30: 90,
         63: 31.5}


def example_01(mdict: dict):
    print(' example_02 '.center(80, '='))

    # printing original dictionary
    print("The original dictionary is : " + str(mdict))

    # Sort Dictionary by Value Difference
    # Using sorted() + lambda + abs() + dictionary comprehension
    res = dict(sorted(mdict.items(), key=lambda sub: abs(sub[1][0] - sub[1][1])))

    # printing result
    print("The sorted dictionary : " + str(res))


def example_02(mdict: dict):
    # custom function for sorting
    def sort_by_difference(item):
        key, value = item
        return abs(value[0] - value[1])

    print(' example_02 '.center(80, '='))

    # printing original dictionary
    print("The original dictionary is : " + str(mdict))

    # Sort Dictionary by Value Difference
    # Using items() method and custom function for sorting
    res = dict(sorted(mdict.items(), key=sort_by_difference))

    # printing result
    print("The sorted dictionary : " + str(res))


def find_dict_value_min(sdict: dict):
    """
    Brute force [BF] algorithm to find the minimum value of the dict
    """
    print(' find_dict_value_min '.center(80, '='))

    min_value = float('inf')  # to find a minimum value of a series, set the "best_value" to
                              # some arbitary large value. Set to infinity in this case.
    pos = 0

    for key, value in sdict.items():
        if value < min_value:
            pos = key
            min_value = value

    # Display the final output:
    print(f'[BF] Input value {pos} will get the lowest output value {min_value}')


def find_dict_value_min_efficient(sdict: dict):
    print(' find_dict_value_min_efficient '.center(80, '='))
    _input = min(sdict, key=sdict.get)
    print(f'[Efficient] Input value {_input} will get the lowest output value {sdict[_input]}')


def find_dict_value_max(sdict: dict):
    """
    Brute force [BF] algorithm to find the maximum value of the dict
    """
    print(' find_dict_value_max '.center(80, '='))
    max_value = 0
    pos = 0

    for key, value in sdict.items():
        if value > max_value:
            pos = key
            max_value = value

    # Display the final output:
    print(f'[BF] Input value {pos} will get the highest output value {max_value}')


def find_dict_value_max_efficient(sdict: dict):
    print(' find_dict_value_max '.center(80, '='))
    _input = max(sdict, key=sdict.get)
    print(f'[Efficient] Input value {_input} will get the highest output value {sdict[_input]}')


if __name__ == '__main__':

    example_01(MAIN_DICT)
    example_02(MAIN_DICT)

    find_dict_value_min(SCORE)
    find_dict_value_min_efficient(SCORE)

    find_dict_value_max(SCORE)
    find_dict_value_max_efficient(SCORE)
