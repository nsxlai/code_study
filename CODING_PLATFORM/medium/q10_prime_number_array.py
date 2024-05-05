# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
from typing import List


def solution(n: int) -> List[int]:
    if n <= 0:
        raise ValueError('Prime number starts at 2')
    prime_nums = [2,]  # Need to prefill the list with 2.
    for num in range(n):
        for i in range(2, num):
            print(f'{num=}, {i=}, {num%i=}, {num//i=}')
            if num % i == 0:
                break
            else:
                prime_nums.append(num)
                print(prime_nums)
    # Before returning the list, there are a lot of repeated element. Change data type to set, back to list, and sort
    return sorted(list(set(prime_nums)))


def solution2(n: int) -> List[int]:
    if n <= 1:
        raise ValueError('Prime number starts at 2')
    prime_nums = []
    for num in range(2, n):  # prime number starts with 2
        is_prime = all([num % i for i in range(2, num)])  # if any number is divisible (num%i == 0), num is not prime
        if is_prime:
            prime_nums.append(num)
    return prime_nums


if __name__ == '__main__':
    # Solution1 code is not working as well.
    print(solution2(2000))
    # print(solution2(1))
