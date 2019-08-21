""" Binary search test question #1
    Given a sorted list, find the smallest element that has the key matching its value
"""


def index_equals_value_search_simple(arr):
    for key, value in enumerate(arr):
     if value == key:
       return key
    return -1


def index_equals_value_search(arr):
    start = 0
    end = len(arr) - 1
    while start <= end:
        mid = int(len(arr) / 2)

        # Searching for the half of the array for content
        if arr[mid] == mid:
            return mid
        elif arr[mid] > mid:
            start = mid + 1
        elif arr[mid] < mid:
            end = mid - 1
    return -1
