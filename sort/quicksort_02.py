# Youtube video: https://www.youtube.com/watch?v=RFyLsF9y83c
from random import randint


def create_array(size=10, max=50):
    return [randint(0, max) for _ in range(size)]


def quicksort(a):
    '''applies quicksort to input array, returns sorted array (not in-place)'''
    if len(a) <= 1:
        return a

    smaller, equal, larger = [], [], []
    pivot = a[randint(0, len(a)-1)]

    for x in a:
        if x < pivot:
            smaller.append(x)
        elif x == pivot:
            equal.append(x)
        else:
            larger.append(x)
    print('recursion start')
    return quicksort(smaller) + equal + quicksort(larger)


if __name__ == '__main__':
    arr = create_array()
    print(arr)
    s_arr = quicksort(arr)
    print(s_arr)