# source: https://www.geeksforgeeks.org/bubble-sort/
def bubbleSort(arr):
    n = len(arr)

    # Traverse through all array elements
    for i in range(n):

        # Last i elements are already in place
        for j in range(0, n - i - 1):

            # traverse the array from 0 to n-i-1
            # Swap if the element found is greater
            # than the next element
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]


if __name__ == '__main__':
    arr = [64, 34, 25, 12, 22, 11, 90]
    bubbleSort(arr)
