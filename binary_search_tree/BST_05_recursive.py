# Master source: https://medium.com/@codingfreak/binary-search-tree-bst-practice-problems-and-interview-questions-ea13a6731098
# source: https://www.techiedelight.com/insertion-in-bst/
# source: https://www.techiedelight.com/search-given-key-in-bst/
# source: https://www.techiedelight.com/deletion-from-bst/
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

    def find(self, root, key):
        if root is None:
            print('Key is not found!')
            return

        if key == root.data:
            print(f'Key {key} is found in the binary tree!')
            return True
        elif key <= root.data:
            self.find(root.left, key)
        else:
            self.find(root.right, key)
        return False

    # Helper function to find maximum value node in subtree rooted at ptr
    def maximumKey(self, curr):
        while curr.right is not None:
            curr = curr.right
        return curr

    # Function to delete node from a BST
    def deleteNode(self, root, key):
        # base case: key not found in tree
        if root is None:
            return root

        # if given key is less than the root node, recur for left subtree
        if key < root.data:
            root.left = self.deleteNode(root.left, key)

        # if given key is more than the root node, recur for right subtree
        elif key > root.data:
            root.right = self.deleteNode(root.right, key)

        # key found else
        # Case 1: node to be deleted has no children(it is a leaf node)
        if root.left is None and root.right is None:
            # update root to null
            return None

        # Case 2: node to be deleted has two children
        elif root.left and root.right:
            # find its in -order predecessor node
            predecessor = self.maximumKey(root.left)

            # Copy the value of predecessor to current node
            root.data = predecessor.data

            # recursively delete the predecessor.Note that the predecessor will have at - most one child(left child)
            root.left = self.deleteNode(root.left, predecessor.data)

        # Case 3: node to be deleted has only one child
        else:
            # find child node Node
            child = root.left if root.left else root.right
            root = child
        return root


if __name__ == '__main__':
    keys = [15, 10, 20, 8, 12, 16, 25]
    myTree = BST()
    root = None
    for key in keys:
        root = myTree.insert(root, key)

    myTree.inOrder(root)
    print()
    myTree.find(root, 18)
    print()
    myTree.find(root, 12)
    print()
    myTree.deleteNode(root, 16)
    print()
    myTree.inOrder(root)