import pdb
import time
from pytest import mark


# def lengthOfLongestSubstring(s: str):
#     temp_str = ''
#     sub_str = []
#     for index1, char1 in enumerate(s):
#         for index2, char2 in enumerate(s):
#             if index1 != index2:
#                 print(f'char1 = {char1}; char2 = {char2}')
#                 print(f'index1 = {index1}; index2 = {index2}')
#                 time.sleep(3)
#                 if char1 != char2:
#                     print('passing')
#                     pass
#                 elif char1 == char2:
#                     print(f'repeat starts')
#                     sub_str.append(s[index1:index2])
#     return sub_str


def lengthOfLongestSubstring(s: str) -> int:
    window = ''
    longest_str = ''
    for i_key, i_value in enumerate(s):
        window = i_value  # starting character
        for j in s[i_key+1:]:
            if j not in window:
                window += j
                # print(f'window = {window}')
            else:
                break
        if len(window) > len(longest_str):
            longest_str = window
    return longest_str, len(longest_str)


@mark.parametrize('input_str, result',
                  [('abcabcbb', ('abc', 3)), ('bbbbbbbb', ('b', 1)),
                   ('pwwkew', ('wke', 3)), ('abdeekdlslrldjsjabcdeabcdeabcdewizifdlelkskd', ('abcdewiz', 8)),
                   (' ', (' ', 1)), ('dvdf', ('vdf', 3))])
def test_lengthOfLongestSubstring(input_str, result):
    assert lengthOfLongestSubstring(input_str) == result


if __name__ == '__main__':
    s1 = 'abcabcbb'
    s2 = 'bbbbbbbb'
    s3 = 'pwwkew'
    s4 = 'abdeekdlslrldjsjabcdeabcdeabcdewizifdlelkskd'
    s5 = ' '
    s6 = 'dvdf'
    test_list = [s1, s2, s3, s4, s5, s6]
    for s in test_list:
        result = lengthOfLongestSubstring(s)
        print(result)
        print('-' * 40)
