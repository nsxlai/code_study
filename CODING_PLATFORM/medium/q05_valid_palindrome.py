# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27


def solution(s: str) -> bool:
    # CASE 1: the string length is even
    for i in range(len(s)):
        t = s[:i] + s[i+1:]  # skipping the ith element for the input string s
        print(f'{t=}')
        if t == t[::-1]:
            return True

    # CASE 2: the string length is odd
    return s == s[::-1]


if __name__ == '__main__':
    s = ['radkar', 'racecar', 'teststr', 'deadbeef', 'abcdefgedcba']
    for i in s:
        print(solution(i))
        print('-' * 20)
