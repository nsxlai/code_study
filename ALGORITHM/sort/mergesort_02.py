# Youtube video: https://www.youtube.com/watch?v=3aTfQvs-_hA
# 1. Array of length n is repeatedly split in half until we are left with n arrays of length 1
# 2. After cocmplete deconstruction, arrays are recombined but not in their original order, they are recombined
#    in sorted order
# 3. We must maintain this tree-like structure in memory, meaning we no longer have constant memory consumption
#    (as in the 3 prior sorting techniques).
#
# There are 2 phases to mergesort:
# 1. Dividing phase: O(log n)
# 2. Recombination phase: O(n)
# Therefore, the time complexity is O(n log n), space complexity is O(n)


def create_array(size=10, max=50):
    from random import randint
    return [randint(0, max) for _ in range(size)]


def merge(a, b):
    c = []
    a_idx, b_idx = 0, 0
    while a_idx < len(a) and b_idx < len(b):
        if a[a_idx] <= b[b_idx]:
            c.append(a[a_idx])
            a_idx += 1
        else:
            c.append(b[b_idx])
            b_idx += 1

    if a_idx == len(a):
        c.extend(b[b_idx:])
    else:
        c.extend(a[a_idx:])
    return c


def merge_sort(a):
    # a list of zero or one elements is sorted, by definition
    if len(a) <= 1:
        return a

    # split the listin half and call merge_sort recursively on teach half
    # Double // will allow returning int instead of float, which is the default for python3 for any division operation
    left, right = merge_sort(a[:len(a)//2]), merge_sort(a[len(a)//2:])

    # merge the now-sorted sublists
    return merge(left, right)


if __name__ == '__main__':
    a = create_array()
    print(a)
    s = merge_sort(a)
    print(s)