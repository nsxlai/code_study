import sys


class Node:
    def __init__(self, data):
        self.right = self.left = None
        self.data = data


class Solution:
    def insert(self, root, data):
        if root is None:
            return Node(data)
        else:
            if data <= root.data:
                cur = self.insert(root.left, data)
                root.left = cur
            else:
                cur = self.insert(root.right, data)
                root.right = cur
        return root

    def levelOrder(self, root):
        #Write your code here
        queue = []
        if root is None:
            return
        queue.append(root)

        while queue:
            current = queue[0]
            # print(f'current.data = {queue[0].data}')
            print(queue[0].data, end=' ')
            if current.left:
                queue.append(current.left)
                # print(f'current.left = {current.left.data}')
            if current.right:
                queue.append(current.right)
                # print(f'current.right = {current.right.data}')
            queue.pop(0)  # Remove the first element


if __name__ == '__main__':
    # T=int(input())
    # data = int(input())
    data = [3, 5, 4, 7, 2, 1]
    myTree = Solution()
    root = None

    for i in range(len(data)):
        root = myTree.insert(root, data[i])

    myTree.levelOrder(root)
