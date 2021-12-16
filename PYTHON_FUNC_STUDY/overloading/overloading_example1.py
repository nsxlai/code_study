"""
source: https://towardsdatascience.com/make-your-python-code-fluent-7ee2dd7c9ae3
   Function overloading study
"""
from multipledispatch import dispatch
import math


@dispatch(str)
def is_palindrome(s: str) -> bool:
    return s == s[::-1]


@dispatch(int)
def is_palindrome(x: int) -> bool:
    temp_x = x
    out_num = 0
    if x < 0:
        return False
    while temp_x > 0:
        p = temp_x % 10
        out_num = out_num * 10 + p
        temp_x = temp_x // 10
        # print('{}, {}, {}, {}'.format(p, out_num, temp_x, x))
    return x == out_num


@dispatch(int,int)
def triangle_area(base, height):
    return (base * height)/2


@dispatch(int,int,int)
def triangle_area(a_side, b_side, c_side):
    s = (a_side + b_side + c_side) / 2
    return math.sqrt(s * (s-a_side) * (s-b_side) * (s-c_side))


if __name__ == '__main__':
    test_list = [121, -121, 234, 2345432, 0, 10, 'abcba', 'abced']
    for item in test_list:
        print(f'{item} is Palindorme? {is_palindrome(item)}')

    print('-' * 25)
    area1 = triangle_area(10, 14)
    area2 = triangle_area(5, 5, 5)
    print(f"Area1: {area1:.2f}")
    print(f"Area2: {area2:.2f}")
