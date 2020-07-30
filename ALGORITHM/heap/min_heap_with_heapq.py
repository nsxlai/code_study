# Source: https://www.geeksforgeeks.org/min-heap-in-python/?ref=leftbar-rightbar
# Python3 program to demonstrate working of heapq

from heapq import heapify, heappush, heappop


if __name__ == '__main__':
    # Creating empty heap
    heap = []
    heapify(heap)

    # Adding items to the heap using heappush function
    heappush(heap, 10)
    heappush(heap, 30)
    heappush(heap, 20)
    heappush(heap, 400)

    # printing the value of minimum element
    print("Head value of heap : " + str(heap[0]))

    # printing the elements of the heap
    print("The heap elements : ")
    for i in heap:
        print(i, end=' ')
    print("\n")

    element = heappop(heap)

    # printing the elements of the heap
    print("The heap elements : ")
    for i in heap:
        print(i, end=' ')