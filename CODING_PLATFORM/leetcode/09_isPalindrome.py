def isPalindrome(x: int) -> bool:
    """
    Try to do this without convert the input integer to string
    :param x:
    :return: boolean
    """
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


if __name__ == '__main__':
    test_list = [121, -121, 234, 2345432, 0, 10]
    for num in test_list:
        print(f'{num} is Palindorme? {isPalindrome(num)}')
