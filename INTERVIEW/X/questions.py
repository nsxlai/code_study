'''
Coding Questions:

1)
name = ‘Morten’
# Print the last element of the variable ‘name’
# Reverse the variable ‘name’

from typing import Tuple
def reverse(name: str) -> Tuple[str, str]:
    return name[-1], name[::-1]


2)
A = ‘Obi Wan’
B = ‘Kenobi’

# Swap the variables A and B
A, B = B, A



3)
# Implement the following function to find the biggest odd number in a list and return it
def find_biggest_odd_number(list_in):
    return max([i for i in list_in if i % 2 != 0])

find_biggest_odd_number([1, 2, 3, 4, 5])


4)
# Sorting lists
def list_sorter(list_in):
    list_in.sort()
    return list_in


unsorted_list = [1, 5, 2]
new_sorted_list = list_sorter(unsorted_list)

# What is the outcome of the function above?
Unsorted_list: [1, 5, 2]
New_sorted_list: [1, 2, 5]

# How to test list_sorter?
    1. Coming up with several* list with various length, e.g., length = 10, 100, 1000,...
    2. Coming up with user error case, e.g., input a list with string element
    3. Coming up with several integer element types, e.g., -1, 0, +100, $100, float number, etc.


5)
names = [‘Bob’, ‘Bo’, ‘Bobby’]
ages = [31, 56, 21]
# Given 2 lists of values - how to convert those to a lookup table?
Lookup_table = dict(zip(names, ages))

Backup solution:
Lookup_table = {*names, *ages}


6)
Ip_address = “192.168.1.23”
# verify that this is a proper IP address

def verify_ip_addr(ip_addr: str) -> bool:
    temp_list = ip_addr.split(‘.’)
    for octet in temp_list:
        if not (0 <= octect < 256):
            return False
    return True


7)
'''
# Please review the function below
def find_averages(list_a, list_b, list_c):
    sum_a = 0
    sum_b = 0
    sum_c = 0
    for i in range(len(list_a)):
        sum_a += list_a[i]
    for i in range(len(list_b)):
        sum_b += list_b[i]
    for i in range(len(list_c)):
        sum_c += list_c[i]

    return sum_a / len(list_a), sum_b / len(list_b), sum_c / len(list_c)


from typing import List, Tuple
from functools import reduce


def find_averages_refactored1(list_a: List[int], list_b: List[int], list_c: List[int]) -> Tuple[float, float, float]:
    """
    Docstring here
    :param list_a: 
    :param list_b: 
    :param list_c: 
    :return: 
    """
    t_func = lambda x, y: x + y
    avg_a = reduce(t_func, list_a) / len(list_a)
    avg_b = reduce(t_func, list_b) / len(list_b)
    avg_c = reduce(t_func, list_c) / len(list_c)
    return avg_a, avg_b, avg_c


def find_averages_refactored2(list_a: List[int], list_b: List[int], list_c: List[int]) -> Tuple[float, float, float]:
    """
    Docstring here
    :param list_a:
    :param list_b:
    :param list_c:
    :return:
    """
    avg_a = sum(list_a) / len(list_a)
    avg_b = sum(list_b) / len(list_b)
    avg_c = sum(list_c) / len(list_c)
    return avg_a, avg_b, avg_c


if __name__ == '__main__':
    a = [1, 2, 3, 4, 5]
    b = [10, 20, 30]
    c = [3, 5, 9, 11, 13, 17]
    avg_a, avg_b, avg_c = find_averages_refactored1(a, b, c)
    print(f'{avg_a=}, {avg_b=}, {avg_c=}')
