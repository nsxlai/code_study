from collections import Counter


def is_anagram(string1, string2):
    return Counter(string1) == Counter(string2)


if __name__ == '__main__':
    print(is_anagram('race', 'care'))
    print(Counter('this is a test'))
