# source: https://www.tutorialspoint.com/data_structures_algorithms/tower_of_hanoi_in_c.htm
# The code was written in C. Translate it to Python
from typing import List


def display() -> None:
    print('[', end='')
    for val in arr:
        print(val, end=' ')
    print(']')


def bubbleSort(arr: List[int]) -> None:
    ''' The nature of bubble sort will first sort the largest number to the end at each iteration.
        At the beginning of each iteration, the sort range is decreased by 1 due to the reason end
        of the array is sorted
    '''
    for i in range(len(arr) - 1):
        swapped = False

        # loop through numbers falling ahead
        for j in range(len(arr) - 1 - i):
            print(f'Items compared: [ {arr[j]}, {arr[j + 1]} ] ', end=' ')

        # check if next number is lesser than current no swap the numbers.
        # (Bubble up the highest number)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]

                swapped = True
                print(f' => swapped [{arr[j]}, {arr[j + 1]}]')
            else:
                print(' => not swapped')

        # if no number was swapped that means array is sorted now, break the loop
        if not swapped:
            break

        print(f'Iteration {i}: ', end='')
        display()
        print('-' * 40)


if __name__ == '__main__':
    arr = [1, 8, 4, 6, 0, 3, 5, 2, 7, 9]
    print("Input Array: ")
    display()
    print()
    bubbleSort(arr)  # in-place sort
    print()
    print('Output Array: ')
    display()
