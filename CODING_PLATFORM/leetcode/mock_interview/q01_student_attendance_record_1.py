"""
You are given a string representing an attendance record for a student. The record only contains the following three characters:
'A' : Absent.
'L' : Late.
'P' : Present.
A student could be rewarded if his attendance record doesn't contain more than one 'A' (absent) or more than two continuous 'L' (late).

You need to return whether the student could be rewarded according to his attendance record.

Example 1:
Input: "PPALLP"
Output: True
Example 2:
Input: "PPALLL"
Output: False
"""
import re


def checkRecord(s: str) -> bool:
    reward = True
    late_regex = re.compile(r'L{3,}')  # more than 3 L in the roll will result no reward
    m = late_regex.search(s)  # search for more than 3 L pattern in the input string

    if s.count('A') > 1 or m:
        reward = False
        return reward
    return reward


if __name__ == '__main__':
    test_list = ['PPALLP', 'PPALLL', 'LALL']
    for s in test_list:
        print(f'{s} record check; reward? {checkRecord(s)}')
