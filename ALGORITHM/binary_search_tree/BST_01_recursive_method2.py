class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinarySearchTreeRecursive:
    def insert(self, root, data):
        if root is None:
            print(f'Adding data {data} at the leaf')
            root = Node(data)
            return root

        if data <= root.data:
            print(f'insert to the left recursively; data = {data}')
            root.left = self.insert(root.left, data)
        else:
            print(f'insert to the right recursively; data = {data}')
            root.right = self.insert(root.right, data)
        return root


def preOrder(root):
    if root is None:
        return
    print(root.data, end=" ")
    preOrder(root.left)
    preOrder(root.right)


if __name__ == '__main__':
    arr = [3, 5, 2, 1, 4, 6, 7]

    tree = BinarySearchTreeRecursive()
    root = None
    for i in arr:
        root = tree.insert(root, i)
    print('Use the BST insert method recursively')
    preOrder(root)