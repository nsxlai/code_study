"""
This example is taken from ALGORITHM/binary_search/binary_search_03.py

Given an array of numbers sorted in ascending order.
Find the element in the array that has the minimum difference with the given key.
For example: min(arr[i] - i)
"""
from typing import List
from random import randint


def find_min_diff(arr: List[int], key: int) -> int:
    min_diff = float('inf')
    low = 0
    high = len(arr) - 1

    while low <= high:
        mid = int((low + high) / 2)
        diff = abs(arr[mid] - key)
        diff_next = abs(arr[mid + 1] - key)
        # print("low = {}; high = {}".format(low, high))
        # print("diff = {}; diff_next = {}".format(diff, diff_next))
        if diff == 0:
            return arr[mid]
        elif diff_next == 0:
            return arr[mid+1]
        # Finding the trend

        elif diff > diff_next:
            low = mid + 1
            min_diff = min(arr[low], arr[low+1], arr[mid])
            # print(f'low = {low}; min_diff = {min_diff}')
        elif diff < diff_next:
            high = mid - 1
            min_diff = arr[high]
            # print(f'high = {high}; min_diff = {min_diff}')
    return min_diff


if __name__ == '__main__':
    # arr = [randint(0, 100) for _ in range(10)]
    # arr.sort()
    arr = [6, 12, 16, 25, 46, 47, 47, 48, 85, 100]
    # key = randint(0, 100)
    key = 56
    print(f'{arr = }, {key = }')

    print(f'{find_min_diff(arr, key) = }')
