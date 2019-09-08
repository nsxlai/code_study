class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Solution:
    def insert(self,head,data):
            p = Node(data)
            if head is None:
                head = p
            elif head.next is None:
                head.next = p
            else:
                start=head
                while start.next is not None:
                    start = start.next
                start.next = p
            return head
    def display(self, head):
        current = head
        while current:
            print(current.data, end=' ')
            current = current.next

    def removeDuplicates(self, head):
        # Write your code here
        if head is None:
            return

        current = head
        # print(f'current.data = {current.data}')
        while current:
            while current.data == current.next.data:
                print(f'current.data = {current.data}')
                print(f'current.next.data = {current.next.data}')
                # prev = current
                # current = current.next
                if current == head:
                    head = current.next  # in case of repeating element in the beginning of the list
                    self.display(head)
                    print('reassigning head')
                    current = current.next
                else:
                    print('non-head repeating')
                    # if current.next.next:
                    current = current.next.next
                    # else:
                    #     current.next = None
                    print(f'current.data = {current.data}')
                    self.display(head)
                    current = current.next
            print('advance to next unique number in the list')
            current = current.next
        return head


if __name__ == '__main__':
    mylist= Solution()
    # T=int(input())
    # data = [1, 2, 2, 3, 3, 4]
    # data = [2, 2, 2, 2, 2, 2, 3, 3, 4]
    data = [2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3]
    head = None

    for i in range(len(data)):
        head = mylist.insert(head, data[i])
    # mylist.display(head)

    head = mylist.removeDuplicates(head)
    mylist.display(head)
