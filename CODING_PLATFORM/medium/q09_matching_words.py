# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
# source: https://www.geeksforgeeks.org/sets-in-python/
# Given two sentences, return an array that has the words that appear in one sentence and
# not the other and an array with the words in common.
from typing import Tuple, List


def solution(s1: str, s2: str) -> Tuple[List[str]]:
    set1 = set(s1.split())
    set2 = set(s2.split())
    # '^' is the symmetric_difference (the set of elements in precisely one of s1 or s2)
    # '&' is the intersection, same as (set1 and set2)
    return sorted(list(set1 ^ set2)), sorted(list(set1 & set2))


if __name__ == '__main__':
    sentence1 = 'We are really pleased to meet you in our city'
    sentence2 = 'The city was hit by a really heavy storm'

    print(solution(sentence1, sentence2))
