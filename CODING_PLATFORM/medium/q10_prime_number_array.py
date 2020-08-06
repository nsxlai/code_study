# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
from typing import List


def solution(n: int) -> List[int]:
    if n <= 0:
        raise ValueError('Prime number starts at 2')
    prime_nums = []
    for num in range(n):
        for i in range(2, num):
            # print(f'{num=}, {i=}')
            if num % i == 0:
                break
            else:
                prime_nums.append(num)
                # print(prime_nums)
    # Before returning the list, there are a lot of repeated element. Change data type to set, back to list, and sort
    return sorted(list(set(prime_nums)))


if __name__ == '__main__':
    n = 10
    print(solution(n))
