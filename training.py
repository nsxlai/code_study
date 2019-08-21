import time
import pdb


def index_equals_value_search1(arr):
    """if index == arr[index], return the smallest index"""
    for key, value in enumerate(arr):
        if value == key:
            return value
    return -1


def index_equals_value_search2(arr):
    """if index == arr[index], return the smallest index"""
    start = 0
    end = len(arr) - 1
    while start <= end:
        mid = int((end + start)/2)
        print('mid = {}'.format(mid))
        if arr[mid] == mid:
            return mid
        elif arr[mid] < mid:
            start = mid + 1
        elif arr[mid] > mid:
            end = mid - 1
    return -1


def SNode:
    def __init__(self, data=None, next=None):
        self.data = data
        self.next = next
    def __repr__(data):
        return repr(self.data)


def Linkedlist:
    def __init__(self):
        self.head = None

    def __repr__(self):
        nodes = []
        curr = self.head
        while curr:
            nodes.append(repr(curr))
            curr = curr.next
        return '[' + ', '.join(nodes) + ']'

    def append(self, data):
        if not self.head:
            self.head = SNode(data=data)
        self.head = curr
        while curr:
            curr = curr.next
        curr.next = SNode(data=data)

    def prepend(self, data):
        self.head = SNode(data=data, next=self.head)

    def insert(self, data):
        pass
    def delete(self, data):
        pass


def subarraySum(nums, k):
    solution_count = 0
    for idx, val in enumerate(nums):
        if nums[idx + 1] <= (len(nums) - 1):
            if k == (nums[idx] + nums[idx+1]):
                solution_count += 1
    return solution_count


if __name__ == '__main__':
    # arr = [-8, -2, 0, 2, 3, 5, 10]
    # result = index_equals_value_search2(arr)
    # print(result)
    result = subarraySum([1, 1, 1], 2)
    print(result)