"""
source: https://towardsdatascience.com/two-pointer-technique-solving-array-problems-at-light-speed-56a77ee83d16

This problem also appears in CODING_PLATFORM/leetcode/11_container_with_most_water.py

In this example, the input list does not need to be sorted before passing to the function
"""
from typing import List, Tuple
from random import randint


def maxArea(height: List[int]) -> Tuple[int, int, int]:
    """
    Use the hint from the LeetCode solution, will move both pointers from the beginning and the end toward the center
    of the list

    Initially we consider the area constituting the exterior most lines. Now, to maximize the area, we need to
    consider the area between the lines of larger lengths. If we try to move the pointer at the longer line
    inwards, we won't gain any increase in area, since it is limited by the shorter line. But moving the shorter
    line's pointer could turn out to be beneficial, as per the same argument, despite the reduction in the width.
    This is done since a relatively longer line obtained by moving the shorter line's pointer might overcome the
    reduction in area caused by the width reduction.

    TIME COMPLEXITY = O(n)
    SPACE COMPLEXITY = O(1)

    :param height:
    :return:
    """
    max_area = 0
    s = idx1 = 0
    e = idx2 = len(height) - 1

    while s < e:
        area = min(height[s], height[e]) * (e - s)
        # max_area = max(area, max_area)
        if area > max_area:
            max_area = area
            idx1, idx2 = s, e
        if height[s] < height[e]:
            s += 1
        else:
            e -= 1
    return max_area, idx1, idx2


if __name__ == '__main__':
    test_list = [randint(1, 100) for _ in range(10)]
    print(f'test_list = {test_list}')
    print(f'Max water area for the list is {maxArea(test_list)}')
