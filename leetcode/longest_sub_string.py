import pdb
import time


def lengthOfLongestSubstring(s: str):
    temp_str = ''
    sub_str = []
    for index1, char1 in enumerate(s):
        for index2, char2 in enumerate(s):
            if index1 != index2:
                print(f'char1 = {char1}; char2 = {char2}')
                print(f'index1 = {index1}; index2 = {index2}')
                time.sleep(3)
                if char1 != char2:
                    print('passing')
                    pass
                elif char1 == char2:
                    print(f'repeat starts')
                    sub_str.append(s[index1:index2])
    return sub_str


if __name__ == '__main__':
    s1 = 'abcabcbb'
    s2 = 'bbbbbbbb'
    s3 = 'pwwkew'
    s4 = 'abdeekdlslrldjsjabcdeabcdeabcdewizifdlelkskd'
    result = lengthOfLongestSubstring(s1)
    print(result)
