class Node:
    def __init__(self, info):
        self.info = info
        self.left = None
        self.right = None
        self.level = None

    def __str__(self):
        return str(self.info)


def preOrder(root):
    if root is None:
        return
    print(root.info, end=" ")
    preOrder(root.left)
    preOrder(root.right)


class BinarySearchTree:
    def __init__(self):
        self.root = None

    # Node is defined as
    # self.left (the left child of the node)
    # self.right (the right child of the node)
    # self.info (the value of the node)

    def insert(self, val):
        #Enter you code here.
        if self.root is None:
            self.root = Node(val)
            self.root.level = 0
            print(f'root.info = {self.root.info}')
            print(f'root.level = {self.root.level}')
            return

        current = self.root
        counter = 1
        print('-' * 45)
        print('start insert')
        print(f'root.info = {current.info}')
        print(f'root.left = {current.left}')
        print(f'root.right = {current.right}')
        print(f'next node value = {val}')
        print('Skipping through Nodes')
        while True:
            if val < current.info:
                print('left side')
                if current.left is None:
                    break
                else:
                    current = current.left
            elif val > current.info:
                print('right side')
                if current.right is None:
                    break
                else:
                    current = current.right
            counter += 1
        print()
        print(f'current.info = {current.info}')
        print(f'current.left = {current.left}')
        print(f'current.right = {current.right}')
        print(f'current.level = {current.level}')
        if val < current.info:
            current.left = Node(val)
            current = current.left
            current.level = counter
            print(f'add {val} to the left side')
            print(f'current.level = {current.level}')
        elif val > current.info:
            current.right = Node(val)
            current = current.right
            current.level = counter
            print(f'add {val} to the right side')
            print(f'current.level = {current.level}')


if __name__ == '__main__':
    tree = BinarySearchTree()
    # t = int(input())
    t = 6
    # arr = list(map(int, input().split()))
    # arr = [4, 2, 3, 1, 7, 6]
    # arr = [7, 9, 4, 2, 6, 3, 5, 1, 8]
    arr = [15, 13, 9, 5, 20, 19, 2, 10, 14, 16, 18, 7, 3, 1]

    for i in range(len(arr)):
        tree.insert(arr[i])

    preOrder(tree.root)
