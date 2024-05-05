"""
Given n non-negative integers a1, a2, ..., an , where each represents a point at coordinate (i, ai).
n vertical lines are drawn such that the two endpoints of line i is at (i, ai) and (i, 0). Find two
lines, which together with x-axis forms a container, such that the container contains the most water.

Note: You may not slant the container and n is at least 2.
"""
from typing import List


def maxArea(height: List[int]) -> int:
    """
    This solution will exceed the leetcode time limit

    TIME COMPLEXITY = O(n^2)
    SPACE COMPLEXITY = O(1)

    :param height:
    :return:
    """
    max_area = 0
    for idx1, val1 in enumerate(height):
        for idx2, val2 in enumerate(height):
            area = min(val1, val2) * (idx2 - idx1)
            # print(f'{val1=}, {val2=}, {idx1=}, {idx2=}, {area=}')

            if area > max_area:
                max_area = area
                # print(f'set max_area = {max_area}')
    return max_area


def maxArea1(height: List[int]) -> int:
    """
    The list comprehension method still take too long
    :param height:
    :return:
    """
    areas = [min(val1, val2) * (idx2 - idx1) for idx1, val1 in enumerate(height) for idx2, val2 in enumerate(height)]
    return max(areas)


def maxArea2(height: List[int]) -> int:
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
    s = 0
    e = len(height) - 1

    while s < e:
        area = min(height[s], height[e]) * (e - s)
        max_area = max(area, max_area)
        if height[s] < height[e]:
            s += 1
        else:
            e -= 1
    return max_area


if __name__ == '__main__':
    test_list = [1, 8, 6, 2, 5, 4, 8, 3, 7]
    print(f'Max Area = {maxArea(test_list)}')
    print(f'Max Area = {maxArea1(test_list)}')
    print(f'Max Area = {maxArea2(test_list)}')
