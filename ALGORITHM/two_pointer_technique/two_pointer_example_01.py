"""
source: https://towardsdatascience.com/two-pointer-technique-solving-array-problems-at-light-speed-56a77ee83d16


Two-sum problem: find which of two elements in an array adds to another number.
The brute force solution would be to run through every possible pair of elements,
a solution that runs in O(n²) time. However, we can use two-pointer to narrow the
runtime to O(n), a drastic speedup. Note that technically, the runtime has been
limited to O(n log n), which is the runtime of the fastest sorting algorithms

These examples require the input list to be pre-sorted before passing the List into the function
"""
from typing import List
from random import randint


def find_largest_two_sum(arr: List) -> int:
    s, e = 0, len(arr)-1
    max_sum = 0
    while s < e:
        max_sum = max(max_sum, arr[s] + arr[e])
        if arr[s] < arr[e]:
            s += 1
        else:
            e -= 1
    return max_sum


def find_target_sum(arr: List[int], target: int) -> bool:
    s, e = 0, len(arr)-1
    while s < e:
        temp_sum = arr[s] + arr[e]
        if temp_sum == target:
            return True
        elif temp_sum < target:
            if arr[s] <= arr[e]:
                s += 1
            else:
                e -= 1
        else:
            if arr[s] <= arr[e]:
                e -= 1
            else:
                s += 1
    return False


if __name__ == '__main__':
    # test_list = [randint(1, 100) for _ in range(10)]
    test_list = [9, 15, 10, 63, 53, 55, 3, 97, 33, 35]
    print(f'test_list = {test_list}')
    test_list.sort()
    print(f'Sorted test_list = {test_list}')
    print(f'The largest sum from the given list is {find_largest_two_sum(test_list)}')
    print(f'The sum of 2 numbers in the list equals to 19: {find_target_sum(test_list, 13)}')
    print(f'The sum of 2 numbers in the list equals to 58: {find_target_sum(test_list, 58)}')
