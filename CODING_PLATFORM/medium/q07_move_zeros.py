# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
# Given an array nums, write a function to move all the zeros to the end of it while maintaining the relative order
# of the non-zero elements.
from typing import List, Deque
from queue import deque


def solution1(nums: List[int]) -> List[int]:
    for i in nums:
        if 0 in nums:
            nums.remove(0)
            nums.append(0)
    return nums


def solution2(nums: List[int]) -> Deque[int]:
    """
    Using deque.rotate will achieve the same goal; however, will get the following runtime error:
    RuntimeError: deque mutated during iteration. Deque data structure cannot be altered during the
    looping process
    :param nums:
    :return:
    """
    dq = deque(nums)
    for i in dq:
        if 0 in dq:
            dq.rotate(1)
    return dq


if __name__ == '__main__':
    array1 = [0, 1, 0, 3, 12]
    array2 = [1, 7, 0, 0, 8, 0, 10, 12, 0, 4]

    for array in [array1, array2]:
        print(solution1(array))
        # print(solution2(array))
