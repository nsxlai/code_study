# Youtube video: https://www.youtube.com/watch?v=CB_NCoxzQnk
# Quick sort is recursive
# It is divide-and-conquer algorithm
# very efficient for large data sets
# Worse case time complexity is O(n^2); average case is O(n log n)
# Performance depends largely on Pivot selection


def quick_sort(A):
    quick_sort2(A, 0, len(A)-1)


def quick_sort2(A, low, hi):
    if low < hi:
        p = partition(A, low, hi)
        quick_sort2(A, low, p-1)
        quick_sort2(A, p+1, hi)


def get_pivot(A, low, hi):
    mid = (hi + low) // 2
    pivot_list = []
    # pivot = hi
    # if A[low] < A[mid]:
    #     if A[mid] < A[hi]:
    #         pivot = mid
    # if A[low] > A[hi]:
    #     pivot = low
    pivot_list.append(A[low])
    pivot_list.append(A[mid])
    pivot_list.append(A[hi])
    pivot_list.pop(pivot_list.index(max(pivot_list)))
    pivot_list.pop(pivot_list.index(min(pivot_list)))
    pivot = pivot_list[0]
    return pivot


def partition(A, low, hi):
    pivotIndex = get_pivot(A, low, hi)
    pivotValue = A[pivotIndex]
    A[pivotIndex], A[low] = A[low], A[pivotIndex]
    border = low

    for i in range(low, hi+1):
        if A[i] < pivotValue:
            border += 1
            A[i], A[border] = A[border], A[i]
    A[low], A[border] = A[border], A[low]
    return border


if __name__ == '__main__':
    arr = [19, 13, 22, 46, 32, 45, 42, 37, 35, 3]
    p = get_pivot(arr, 0, len(arr)-1)
    print(p)