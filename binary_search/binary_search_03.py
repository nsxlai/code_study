"""
Given an array of numbers sorted in ascending order.
Find the element in the array that has the minimum difference with the given key.
For example: min(arr[i] - i)
"""


def find_mind_diff(arr, key):
    low = 0
    high = len(arr) - 1
    # min_diff = abs(arr[0] - 0)
    while low <= high:
        mid = int((low + high) / 2)
        diff = abs(arr[mid] - key)
        diff_next = abs(arr[mid + 1] - key)
        print("low = {}; high = {}".format(low, high))
        print("diff = {}; diff_next = {}".format(diff, diff_next))
        # if diff == min_diff:
        #     return arr[mid]
        # Finding the trend

        if diff > diff_next:
            low = mid + 1
            min_diff = diff_next
            print('low = {}'.format(low))
        elif diff < diff_next:
            high = mid - 1
            min_diff = diff
            print('high = {}'.format(high))
    return arr[mid]
