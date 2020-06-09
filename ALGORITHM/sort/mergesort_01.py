# From youtube video: https://www.youtube.com/watch?v=Nso25TkBsYI
# Mergesort is recursive
# Divide-and-conquer ALGORITHM
# very efficient for large data sets
# Mergesort does log(n) merge steps because each merge step doubles the list size
# It does N work for each merge step because it must look at every item
# So it runs in O(n log(n))

def merge_sort(A):
    merge_sort2(A, 0, len(A)-1)


def merge_sort2(A, first, last):
    if first < last:  # more than 1 element in the list
        middle = (first + last) // 2
        merge_sort2(A, first, middle)
        merge_sort2(A, middle, last)
        merge(A, first, middle, last)


def merge(A, first, middle, last):
    L = A[first:middle]
    R = A[middle:last]
    L.append(999999999)
    R.append(999999999)
    i = j = 0
    for k in range(first, last+1):
        if L[i] <= R[j]:
            A[k] = L[i]
            i += 1
        else:
            A[k] = R[j]
            j += 1