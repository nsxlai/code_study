# Youtube video: https://www.youtube.com/watch?v=uWL6FJhq5fM


class Node:
    def __init__(self, data):
        self.right = self.left = None
        self.data = data


def DFS(root):
    # DFS is a pre-order BST traversal
    if root:
        print(root.data)
        DFS(root.left)
        DFS(root.right)


