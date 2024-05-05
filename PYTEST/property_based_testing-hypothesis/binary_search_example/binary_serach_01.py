""" Binary search test question #1
    Given a sorted list, find the smallest element that has the key matching its value
"""
from typing import List


def index_equals_value_search_simple(arr: List[int]) -> int:
    for key, value in enumerate(arr):
        if value == key:
            return key
    return -1


def index_equals_value_search(arr: List[int]) -> int:
    start = 0
    end = len(arr) - 1
    while start <= end:
        mid = (start + end) // 2

        # Searching for the half of the array for content
        if arr[mid] == mid:
            return mid
        elif arr[mid] > mid:
            end = mid - 1
        elif arr[mid] < mid:
            start = mid + 1
    return -1  # not found


if __name__ == '__main__':
    arr = [-5, -3, 0, 3, 5]
    print(f'{index_equals_value_search(arr) = }')
