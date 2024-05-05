"""
Given a range of numbered days, [i...j] and a number k, determine the number of days in the range that are
beautiful. Beautiful numbers are defined as numbers where |i - reverse(i)| is evenly divisible by k.
If a day's value is a beautiful number, it is a beautiful day. Print the number of beautiful days in the range.

Function Description

Complete the beautifulDays function in the editor below. It must return the number of beautiful days in the range.

beautifulDays has the following parameter(s):

i: the starting day number
j: the ending day number
k: the divisor

Sample Input
20 23 6

Sample Output
2

Lily may go to the movies on days 20, 21, 22, and 23. We perform the following calculations to determine
which days are beautiful:

Day 20 is beautiful because the following evaluates to a whole number: |20 - 2| / 6 = 3
Day 21 is not beautiful because the following doesn't evaluate to a whole number: |21 - 12| / 6 = 1.5
Day 22 is beautiful because the following evaluates to a whole number: |22 - 22| / 6 = 0
Day 23 is not beautiful because the following doesn't evaluate to a whole number: |23 - 32| / 6 = 1.5
Only two days, 20 and 22, in this interval are beautiful. Thus, we print 2 as our answer.
"""


def beautifulDays(i, j, k):
    b_day = 0
    for num in range(i, j+1):
        if abs(num - reverse_num(num)) % k == 0:  # divible
            b_day += 1
    return b_day


def reverse_num(n):
    output = 0
    while n > 0:
        p = n % 10
        output = output * 10 + p
        n = n // 10
    return output


if __name__ == '__main__':
    print(f'{beautifulDays(20, 23, 6)}')
