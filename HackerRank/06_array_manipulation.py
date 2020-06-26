import numpy as np


# Complete the arrayManipulation function below.
def arrayManipulation1(n, queries):
    ''' This is a brute force implementation and has O(n*m) complexity, which
       will fail the HackerRank allowable execution time slow
    '''
    arr = [0 for i in range(n+1)]   # Initialize array with 0 with n+1
    for e in queries:               # elment[1]+1 may be out of range
        for i in range(e[0], e[1]+1):
            arr[i] = arr[i] + e[2]
    return max(arr)


def arrayManipulation2(n, queries):
    ''' Use Numpy matrix manipulation method to optimize the run time; however
        HackerRank environemt does not have Numpy package available
    '''
    arr = np.zeros(n+1)   # Initialize array with 0 with n+1
    for e in queries:     # elment[1]+1 may be out of range
        arr[e[0]:e[1]+1] = arr[e[0]:e[1]+1] + e[2]
    return int(arr.max())


def arrayManipulation3(n, queries):
    ''' source: https://www.youtube.com/watch?v=hDhf04AJIRs
        Use prefix sum algorithm to reduce the complexity from O(m*n) to O(n)
    '''
    arr = [0 for i in range(n+2)]
    for e in queries:
        arr[e[0]] += e[2]
        arr[e[1]+1] -= e[2]
        # print(f'arr1 = {arr}')

    # prefix sum algorithm
    # This algorithm did not reconstruct the entire output array but rather
    # just gather the max value information and return it (more efficient)
    sum, max = 0, 0
    for i in range(len(arr)-1):
        sum += arr[i]  # The sum is accumulative
        max = max(sum, max)
        # print(f'arr2 = {arr}')
    return max


if __name__ == '__main__':
    n = 5
    q = [[1, 2, 100], [2, 5, 100], [3, 4, 100]]
    print(f'q = {q}')
    print(arrayManipulation1(n, q))
    print('-' * 10)
    print(arrayManipulation3(n, q))
