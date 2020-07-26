"""
Implement atoi which converts a string to an integer.

The function first discards as many whitespace characters as necessary until the first non-whitespace character
is found. Then, starting from this character, takes an optional initial plus or minus sign followed by as many
numerical digits as possible, and interprets them as a numerical value.

The string can contain additional characters after those that form the integral number, which are ignored and
have no effect on the behavior of this function.

If the first sequence of non-whitespace characters in str is not a valid integral number, or if no such sequence
exists because either str is empty or it contains only whitespace characters, no conversion is performed.

If no valid conversion could be performed, a zero value is returned.
"""
from pytest import mark
# from typing import Optional, Any
import re


def myAtoi(str: str) -> int:
    out_num = 0
    is_neg = False
    special_case = ['++', '+-', '-+', '--', '+ ', '- ']

    for idx, s in enumerate(str):
        try:
            if s == '+':
                if str[idx:idx+2] in special_case:
                    break
            elif s == '-':
                if str[idx:idx+2] in special_case:
                    break
                is_neg = True
            elif s.isnumeric():  # same as 0 <= int(s) <= 9
                out_num = out_num * 10 + int(s)
                if not str[idx+1].isnumeric():
                    break
            elif s == ' ':  # skip for white space
                continue
            elif s == '.':  # if the number is a decimal
                break
            elif not s.isnumeric():  # if not a number, return the value
                return neg_check(out_num, is_neg)
        except (ValueError, IndexError):
            pass

    out_num = neg_check(out_num, is_neg)
    if out_num < -2 ** 31:
        return -2 ** 31
    elif out_num > (2 ** 31 - 1):
        return 2 ** 31 - 1
    else:
        return out_num


def neg_check(num, is_neg):
    if is_neg:
        num *= -1
    return num


def myAtoi2(str: str) -> int:
    MAX_INT = 2147483647
    MIN_INT = -2147483648

    reg = re.compile("^[+-]?\d*")
    nstr = reg.findall(str.strip())

    if len(nstr) > 0:
        nstr = nstr[0]
    else:
        return 0

    if not nstr or nstr == "-" or nstr == "+":
        return 0

    num = int(nstr)

    if num > MAX_INT:
        return MAX_INT
    elif num < MIN_INT:
        return MIN_INT
    else:
        return num


test_list = [('42', 42), ('   -42', -42), ('4193 with words', 4193),
             ('words and 987', 0), ('-91283472332', -2147483648), ('  3.1415', 3),
             ('+-2', 0), ('-+1', 0), ('010', 10), ('  -0012a42', -12), ('   +0 123', 0),
             ('-   234', 0), ('91283472300', 2147483647), ('00100345', 100345)]


@mark.parametrize('num_in, num_out', test_list)
def test_myAtoi(num_in: str, num_out: int) -> None:
    assert num_out == myAtoi(num_in)


@mark.parametrize('num_in, num_out', test_list)
def test_myAtoi2(num_in: str, num_out: int) -> None:
    assert num_out == myAtoi2(num_in)


if __name__ == '__main__':
    for num_in, num_out in test_list:
        # print(f'original input: {num_in}, expected output: {num_out}, code output: {myAtoi(num_in)}, '
        #       f'Pass/Fail? {num_out==myAtoi(num_in)}')
        print(f'original input: {num_in}, regex output: {regex_find(num_in)}')

