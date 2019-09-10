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

    def insert(self, root, key):
        """ Iterative function to insert an key into BST """
        # Root is passed by reference to the function
        curr = root
        parent = None

        # if tree is empty, create a new node and set root
        if root is None:
            return Node(key)

        # traverse the tree and find parent node of key
        while curr is not None:
            # update parent node as current node
            parent = curr

            # if given key is less than the current node,
            # go to left subtree else go to right subtree
            if key < curr.data:
                curr = curr.left
            else:
                curr = curr.right

        # construct a new node and assign to appropriate parent pointer
        if key <= parent.data:
            parent.left = Node(key)
        else:
            parent.right = Node(key)
        return root


if __name__ == '__main__':
    keys = [15, 10, 20, 8, 12, 16, 25]
    myTree = BST()
    root = None
    for key in keys:
        root = myTree.insert(root, key)

    myTree.inOrder(root)
