"""
Given an array of integers, return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.
"""
from typing import List


def twoSum(nums: List[int], target: int) -> List[int]:
    for i in range(len(nums)):
        complement = target - nums[i]
        # print(f'temp = {temp}')
        # print(f'complement = {complement}')
        if complement in nums[i:]:
            return [i, nums.index(complement)]
    return []


if __name__ == '__main__':
    nums = [2, 7, 11, 15]
    target = 17
    print(twoSum(nums, target))
