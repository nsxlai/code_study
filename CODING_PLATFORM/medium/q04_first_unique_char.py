# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
# Given a string, find the first non-repeating character in it and return its index.
# If it doesn't exist, return -1
from collections import Counter


def solution1(s: str) -> int:
    freq = {}
    for i in s:
        if i not in freq:
            freq.setdefault(i, 1)
        else:
            freq[i] += 1
    print(f'{freq=}')
    for i in range(len(s)):
        if freq[s[i]] == 1:
            return i
    return -1


def solution2(s: str) -> int:
    freq = Counter(s)
    print(f'{freq=}')

    for idx, val in enumerate(s):
        if freq[val] == 1:
            return idx
    return -1


if __name__ == '__main__':
    print(solution1('alphabet'))
    print(solution2('alphabet'))
    print('-' * 20)
    print(solution1('barbados'))
    print(solution2('barbados'))
    print('-' * 20)
    print(solution1('crunchy'))
    print(solution2('crunchy'))
    print('-' * 20)
    print(solution1('industrialization'))
    print(solution2('industrialization'))
    print('-' * 20)
    print(solution1('illustration'))
    print(solution2('illustration'))
