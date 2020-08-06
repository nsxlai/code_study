# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
# Given an array of integers, determine whether the array is monotonic or not.
# Monotonic array is an array that is always increase or always decrease.
from typing import List


def solution(nums: List[int]) -> bool:
    mono_incr = [nums[i] <= nums[i+1] for i in range(len(nums)-1)]  # the loop does not extend to the last element
    mono_desc = [nums[i] >= nums[i+1] for i in range(len(nums)-1)]
    print(f'{mono_incr=}, {mono_desc=}')
    return all(mono_incr) or all(mono_desc)


def solution_simple(nums: List[int]) -> bool:
    return (all(nums[i] <= nums[i+1] for i in range(len(nums)-1)) or  # List comp inside all() or any() doesn't need []
            all(nums[i] >= nums[i+1] for i in range(len(nums)-1)))


if __name__ == '__main__':
    A = [6, 5, 4, 4]
    B = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]
    C = [1, 1, 2, 3, 7]

    print(solution(A))
    print(solution(B))
    print(solution(C))
    print('-' * 20)
    print(solution_simple(A))
    print(solution_simple(B))
    print(solution_simple(C))
