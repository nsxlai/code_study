from math import ceil

def findMedianSortedArrays(nums1, nums2):
    """
    There are two sorted arrays nums1 and nums2 of size m and n respectively.
    Combine both list in the sorted manner.
    Find the median of the two sorted arrays. The overall run time complexity should be O(log (m+n)).
    :param nums1: sorted list 1
    :param nums2: sorted list 2
    :return: c_num (combined list of list 1 and list 2)
    """
    c_nums = []  # combined nums
    i = j = 0
    while i < len(nums1) and j < len(nums2):
        if nums1[i] < nums2[j]:
            c_nums.append(nums1[i])
            i += 1
        elif nums1[i] == nums2[j]:
            c_nums.append(nums1[i])
            c_nums.append(nums2[j])  # Redundent number will appear here; comment this line to show only 1 numbers
            i += 1
            j += 1
        else:
            c_nums.append(nums2[j])
            j += 1
    if i == len(nums1):
        c_nums.extend(nums2[j:])
    if j == len(nums2):
        c_nums.extend(nums1[i:])

    # Now find the medium
    c_nums_len = len(c_nums)
    if is_even(c_nums_len):  # c_num has even elements
        median = (c_nums[c_nums_len//2] + c_nums[c_nums_len//2 - 1]) / 2
    else:
        median = c_nums[c_nums_len//2]
    return c_nums, median


def is_even(l_len):
    status = False
    if l_len % 2 == 0:
        status = True
    return status


if __name__ == '__main__':
    # nums1, nums2 = [1, 3, 5, 7, 9], [2, 4, 6, 8]
    # nums1, nums2 = [1, 2], [3, 4]

    num_list = [([1, 3, 5, 7, 9], [2, 4, 6, 8]),
                ([1, 2], [3, 4]),
                ([1, 4, 7, 9, 10, 20, 23], [3, 11, 15, 20])]
    for nums1, nums2 in num_list:
        print(f'{nums1=}, {nums2=}')
        result = findMedianSortedArrays(nums1, nums2)
        print(result)
        print('-' * 25)
