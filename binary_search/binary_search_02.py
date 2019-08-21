""" From Medium:
https://medium.com/better-programming/three-smart-ways-to-use-binary-search-in-coding-interviews-250ba296cb82

Given an array of numbers, sorted in ascending order. Find the ceiling of a given number “key”.
The ceiling of the key will be the smallest element in the given array, greater than or equal to the key.
"""
import pdb


def find_ceiling(arr, key):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = int((low + high) / 2)  # Python3 will output float after division
        diff = arr[mid] - key
        print('diff #1 = {}'.format(diff))
        # pdb.set_trace()
        if diff == 0:
            return arr[mid]  # Returning the ceiling element; may need to check this condition for edge cases
        elif diff < 0:
            low = mid + 1
            print('low = {}; diff = {}'.format(low, diff))
        elif diff > 0:
            high = mid - 1
    return arr[mid]


if __name__ == '__main__':
    arr = [-5, -2, 0, 1, 4, 7, 9, 12, 15, 20]
    key = 13
    result = find_ceiling(arr, key)
    print(result)