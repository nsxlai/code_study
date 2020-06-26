"""
Lilah has a string, s, of lowercase English letters that she repeated infinitely many times.
Given an integer, n, find and print the number of letter a's in the first  letters of Lilah's infinite string.

For example, if the string s = 'abcac' and n= 10, the substring we consider is 'abcacabcac', the first 10 characters
of her infinite string. There are 4 occurrences of 'a' in the substring.

Function Description
Complete the repeatedString function in the editor below. It should return an integer representing the number of
occurrences of a in the prefix of length n in the infinitely repeating string.

repeatedString has the following parameter(s):

s: a string to repeat
n: the number of characters to consider
"""


# Complete the repeatedString function below.
def repeatedString(s, n):
    s_len = len(s)
    a_cnt = s.count('a')
    s_multiplier = (n // s_len)
    extra_a = 0
    if n % s_len != 0:
        upfill = n - (s_multiplier * s_len)
        # print('upfill = {}'.format(upfill))
        extra_a = s[:upfill].count('a')
    return s_multiplier * a_cnt + extra_a


if __name__ == '__main__':
    s1, n = 'abcac', 10
    print(f'Test Case 1: {repeatedString(s1, n)}')

    s2, n = 'ab', 10
    print(f'Test Case 2: {repeatedString(s2, n)}')

    s3, n = 'abcac', 100
    print(f'Test Case 3: {repeatedString(s3, n)}')

    s4, n = 'a', 1000000000000
    print(f'Test Case 4: {repeatedString(s4, n)}')

    s5, n = 'abc', 10
    print(f'Test Case 5: {repeatedString(s5, n)}')

    s6, n = 'aba', 10
    print(f'Test Case 6: {repeatedString(s6, n)}')

    s7, n = 'aba', 1000000000000
    print(f'Test Case 7: {repeatedString(s7, n)}')
