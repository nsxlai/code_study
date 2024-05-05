# source: https://towardsdatascience.com/10-algorithms-to-solve-before-your-python-coding-interview-feb74fb9bc27
# Given an array containing None values fill in the None values with most recent non-None value in the array
# This is the forward-fill method in Pandas. See pandas Jupyter notebook for detail
from typing import List


def forward_fill(nums: List[int]) -> List[int]:
    """
    Fill the None value with the valid integer from the previous element
    """
    value = 0
    out_list = []
    for i in nums:
        if i is not None:
            out_list.append(i)
            value = i
        else:
            out_list.append(value)
    return out_list


def back_fill(nums: List[int]) -> List[int]:
    """
    Fill the None value with the first valid integer after the None value
    """
    i = value = 0
    out_list = []
    while i < len(nums):
        if nums[i] is not None:
            out_list.append(nums[i])
        else:
            for j in nums[i:]:
                if j is not None:
                    value = j
                    break
            out_list.append(value)
        i += 1
    return out_list


if __name__ == '__main__':
    array1 = [1, None, 2, 3, None, None, 5, None, 3, None, 1, 1, None]
    print(f'Forward Filled: {forward_fill(array1)}')
    print(f'Back Filled: {back_fill(array1)}')
