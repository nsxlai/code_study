"""
Given 2 sorted list, perform a in-place sort on l1 to merge l1 and l2 (sorted)
l1=[1,2,3,0, 0, 0], m = 30,0
l2=[4,5,6],       n = 3
output l1=[1,2,2,3,5,6]

l1 = [1, 4, 2, 3, 0, 0 , 0]
"""


def merge1(l1, m, l2, n):
    while True:
        if l1[-1] == 0:
            l1.pop()
        else:
            break
    print(f'{l1 = }, {l2 = }')
    l1 += l2   # append l2 to the back of l1
    l1.sort()  # perform in-place sort


def merge2(l1, m, l2, n):
    i = j = 0
    while True:
        if l1[-1] == 0:
            l1.pop()
        else:
            break

    while i < (m-n) and j < n:
        if l1[i] <= l2[j]:
            i += 1
        elif l1[i] > l2[j]:
            l1.insert(i, l2[j])
            i += 1
            l2.remove(l2[j])
            j += 1
    l1 += l2


if __name__ == '__main__':
    l1 = [1, 2, 3, 5, 0, 0, 0]
    l2 = [4, 6, 7]
    m = 7  # len(l1)
    n = 3  # len(l2)
    merge1(l1, m, l2, n)
    print(f'{l1 = }')

    l1 = [1, 2, 3, 5, 0, 0, 0]
    l2 = [4, 6, 7]
    merge2(l1, m, l2, n)
    print(f'{l1 = }')
