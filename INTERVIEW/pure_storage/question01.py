# coding interview
# Write a function that adds 2 strings together and return a string version of the answer
# '12' + '34' = '46'
# Cannot use internal tool like int to convert string to integer
from itertools import zip_longest


def addNumbers(a: str, b: str) -> str:
    # sum = int(a, 10) + int(b, 10)  # Original implementation if int() is allowed to use
    # sum = a + b
    num_list = [i for i in range(10)]
    str_list = '0 1 2 3 4 5 6 7 8 9'.split()
    str_num_conv_dict = dict(zip(str_list, num_list))

    # multiplier, final = 0, 0
    overflow_int = 0
    final_str = ''
    for s1, s2 in zip_longest(a[::-1], b[::-1]):
        temp_int1 = str_num_conv_dict.get(s1, 0)
        temp_int2 = str_num_conv_dict.get(s2, 0)
        # final = final + (temp_int1 + temp_int2) * 10**multiplier
        # multiplier += 1
        # print(f'{temp_int1}, {temp_int2}')
        final = temp_int1 + temp_int2 + overflow_int
        overflow_int = final // 10  # Getting the overflow_int (either 0 or 1)
        final %= 10  # Getting the one's digit
        # print(f'{final}, {str(final)}')
        final_str += str(final)
    return final_str[::-1]


def addNumbers2(a: str, b: str) -> str:
    """ This will achieve the same purpose but with less syntax """
    return str(eval(a) + eval(b))


if __name__ == '__main__':
    print(addNumbers('127', '56'))  # 183
    print(addNumbers2('127', '56'))
