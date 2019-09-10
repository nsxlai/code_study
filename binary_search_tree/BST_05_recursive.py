# source: https://www.techiedelight.com/insertion-in-bst/
# the code was originally in JAVA. I have translated the code to Python


class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BST:
    def inOrder(self, root):
        """Function to perform inorder traversal of the tree"""
        if root is None:
            return
        self.inOrder(root.left)
        print(root.data, end=' ')
        self.inOrder(root.right)

    def insert(self, root, data):
        """Recursive function to insert an key into BST"""
        # if the root is null, create a new node an return it
        if root is None:
            # print(f'Adding root node; key = {key}')
            return Node(data)

        # if given key is less than the root node,
        # recur for left subtree
        if data <= root.data:
            # print(f'Insert left node; key = {key}')
            root.left = self.insert(root.left, data)
        else:    # key > root.data
            # print(f'Insert right node; key = {key}')
            root.right = self.insert(root.right, data)
        return root


if __name__ == '__main__':
    keys = [15, 10, 20, 8, 12, 16, 25]
    myTree = BST()
    root = None
    for key in keys:
        root = myTree.insert(root, key)

    myTree.inOrder(root)
