"""
from the input list, create a output list that has the product of the input list excluding
 the element with the same index

for example,
in_lst = [2, 3, 4, 5]

First element of the out_list will be 3 * 4 * 5 = 60, the second element of the out_list will be 2 * 4 * 5 = 40

out_lst = [60, 40, 30, 24]
"""

from functools import reduce


def prod(lst):
    out_lst = []
    cnt = 0
    while cnt < len(lst):
        out_lst.append(reduce(lambda x, y: x * y, lst) // lst[cnt])
        cnt += 1
    return out_lst


if __name__ == '__main__':
    in_lst = [2, 3, 4, 5]
    out_lst = [60, 40, 30, 24]
    print(prod(in_lst))
