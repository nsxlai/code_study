def reverse(x: int) -> int:
    # Initial value
    is_neg = False
    out_int = 0

    # Set is_neg flag and remove the flag
    if x < 0:
        is_neg = True
        x *= -1

    # Divide the original int by 10 and also construct the output_int
    while x > 0:
        p = x % 10
        x = x // 10
        out_int = out_int * 10 + p
        # print(f'{x=}, {p=}, {out_int=}')

    # Put back the negative sign if is_neg is set to True
    if is_neg is True:
        out_int *= -1

    # If the out_int is out of range of 32 bit integer (-2^31, 2^31-1), output 0; else return the out_int
    return 0 if overflow_check(out_int) else out_int


def overflow_check(x: int) -> bool:
    overflow = False
    if any([x < (-2 ** 31), x > (2 ** 31 - 1)]):
        overflow = True
    return overflow


def reverse_new(x: int) -> int:
    """
    source from https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
    :param x:
    :return:
    """
    string = str(x)

    if string[0] == '-':
        out_int = int('-' + string[:0:-1])
    else:
        out_int = int(string[::-1])
    return 0 if overflow_check(out_int) else out_int


if __name__ == '__main__':
    test_list = [123, -456, 1200, 0, 901000, 95123456123456]
    for num in test_list:
        print(f'{num} in reverse: {reverse(num)}')
        print(f'{num} in reverse_new: {reverse_new(num)}')
        print('-' * 30)

