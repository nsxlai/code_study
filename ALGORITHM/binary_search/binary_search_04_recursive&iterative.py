x# Youtube video: https://www.youtube.com/watch?v=P3YID7liBug&feature=youtu.be&t=352s
# The Youtube video example is coding in Java. I have translated into Python code.


def BinarySearchRecursive(arr, x, left, right):
    if left > right:
        return False  # No search result found

    mid = (left + right) // 2
    if arr[mid] == x:
        return True  # Found search result
    elif x < arr[mid]:
        return BinarySearchRecursive(arr, x, left, mid-1)
    else:
        return BinarySearchRecursive(arr, x, mid+1, right)


def BinarySerchIterative(arr, x):
    left = 0
    right = len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == x:
            return True
        elif x < arr[mid]:
            right = mid - 1
        else:
            left = mid + 1
    return False


if __name__ == '__main__':
    arr = [8, 10, 12, 15, 16, 20, 25]
    target = 20

    print(BinarySearchRecursive(arr, target, 0, len(arr)-1))

    print(BinarySerchIterative(arr, target))