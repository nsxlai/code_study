# Master source: https://medium.com/@codingfreak/binary-search-tree-bst-practice-problems-and-interview-questions-ea13a6731098
# source: https://www.techiedelight.com/insertion-in-bst/
# source: https://www.techiedelight.com/search-given-key-in-bst/
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
        """ Iterative function to insert an key into BST """
        # Root is passed by reference to the function
        curr = root
        parent = None

        # if tree is empty, create a new node and set root
        if root is None:
            return Node(data)

        # traverse the tree and find parent node of key
        while curr:
            # update parent node as current node
            parent = curr

            # if given key is less than the current node,
            # go to left subtree else go to right subtree
            if data < curr.data:
                curr = curr.left
            else:
                curr = curr.right

        # construct a new node and assign to appropriate parent pointer
        if data <= parent.data:
            parent.left = Node(data)
        else:
            parent.right = Node(data)
        return root

    def find(self, root, key):
        if root is None:
            print('The key is not found!')
            return False

        current = root
        while current:
            if key == current.data:
                print(f'Key {key} is found is the binary tree!')
                return True
            elif key <= current.data:
                current = current.left
            else:  # key > current.data
                current = current.right
        print(f'Key {key} is not found in the binary tree!')
        return False

    # Helper function to find minimum value node in subtree rooted at curr
    def minimumKey(self, curr):
        while curr.left:
            curr = curr.left
        return curr

    def deleteNode(self, root, key):
        """Function to delete node from a BST"""
        parent = None
        curr = root

        # search key in BST and set its parent pointer
        while curr and curr.data != key:
            # update parent node as current node
            parent = curr

            # if given key is less than the current node, go to left subtree else go to right subtree
            if key < curr.data:
                curr = curr.left
            else:
                curr = curr.right

        # return if key is not found in the tree
        if curr is None:
            return root

        # Case 1: node to be deleted has no children i.e. it is a leaf node
        if curr.left is None and curr.right is None:
            if curr != root:
                # if node to be deleted is not a root node, then set its parent left/right child to null
                if parent.left == curr:
                    parent.left = None
                else:
                    parent.right = None
            else:
                # if tree has only root node, delete it and set root to null
                root = None

        # Case 2: node to be deleted has two children
        elif curr.left and curr.right:
            # find its in-order successor node
            successor = self.minimumKey(curr.right)

            # store successor value
            val = successor.data

            # recursively delete the successor. Note that the successor will have at-most one child (right child)
            self.deleteNode(root, successor.data)

            # Copy the value of successor to current node
            curr.data = val

        # Case 3: node to be deleted has only one child
        else:
            # find child node
            child = curr.left if curr.left else curr.right

            # if node to be deleted is not a root node, then set its parent to its child
            if curr != root:
                if curr == parent.left:
                    parent.left = child
                else:
                    parent.right = child

            # if node to be deleted is root node, then set the root to child
            else:
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
