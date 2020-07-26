"""
Interview Query Question #37 | String Subsequence

This question was asked by: Ike
Given two strings, string1 and string2, find out if string1 is a subsequence of string2.

A subsequence is a sequence that can be derived from another sequence by deleting some elements without changing the order of the remaining elements.

Example:

string1 = 'abc'
string2 = 'asbsc'
string3 = 'acedb'
string4 = 'edvasbdc'

isSubSequence(string1, string2) -> True
isSubSequence(string1, string3) -> False
isSubSequence(string1, string4) -> True
"""


def isSubSequence(str1, str2):
    # first_char, remain_str = str1[0], str1[1:]
    # if str1[0] in str1:
    work_str = ''
    try:
        for idx1, char1 in enumerate(str1):
            for idx2, char2 in enumerate(str2):
                str1_p1, str1_p2 = char1, str1[idx1 + 1:]
                if char1 == char2:
                    print(f'{work_str=}')
                    work_str += char1
                    str2_p1, str2_p2, str2_p3 = char2, str2[idx2+1], str2[idx2+2:]
                    print(f'{str1_p1=}, {str1_p2=}')
                    print(f'{str2_p1=}, {str2_p2=}, {str2_p3=}')
                    if str2_p2 in str1_p2[1:]:  # excluding the first element.
                        return False
                    elif str2_p2 == str1_p2[0]:
                        work_str += str2_p2
    except IndexError:
        pass
    return True


def isSubSequence1(string1, string2):
    prev = 0
    for i in string1:
        if string2.find(i, prev) == -1:
            return False
        else:
            prev = string2.find(i, prev) + 1
    return True


if __name__ == '__main__':
    string1 = 'abc'
    string2 = 'asbsc'
    string3 = 'acedb'
    string4 = 'edvasbdc'
    string5 = 'babekdkiekdjlsascadbwwoieircwodkal'
    string6 = 'effffghi'
    string7 = 'babekdkiecdjl'
    print(isSubSequence1(string1, string2))
    print('-' * 30)
    print(isSubSequence1(string1, string3))
    print('-' * 30)
    print(isSubSequence1(string1, string4))
    print('-' * 30)
    print(isSubSequence1(string1, string5))
    print('-' * 30)
    print(isSubSequence1(string1, string6))
    print('-' * 30)
    print(isSubSequence1(string1, string7))
