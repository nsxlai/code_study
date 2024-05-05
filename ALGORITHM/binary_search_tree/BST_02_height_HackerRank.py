import time


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

    def getHeight(self, root):
        # Write your code here
        if root is None:
            return -1  # if counting edges, need to reduce by 1
        else:
            print(f'root.data = {root.data}')
            height_left = self.getHeight(root.left)
            print(f'left = {height_left}')
            height_right = self.getHeight(root.right)
            print(f'right = {height_right}')

        if height_left >= height_right:
            return height_left + 1
        else:
            return height_right + 1
        # return max(height_left, height_right) + 1

    def getHeight_efficient(self, root):
        # Write your code here
        if root is None:
            return -1  # if counting edges, need to reduce by 1
        return max(self.getHeight(root.left), self.getHeight(root.right)) + 1


if __name__ == '__main__':
    # T=int(input())
    # data = int(input())
    data = [3, 5, 2, 1, 4, 6, 7]
    myTree = Solution()
    root = None
    for i in range(len(data)):
        root = myTree.insert(root, data[i])

    # height = myTree.getHeight(root)
    height = myTree.getHeight_efficient(root)
    print(height)
