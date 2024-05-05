# source: https://towardsdatascience.com/data-structures-algorithms-in-python-68c8dbb19c90
class Node:
    def __init__(self, name: str):
        self.left = None
        self.right = None
        self.name = name


def in_order(root):
    """
    In-order traversal: left -> root -> right
    """
    if root:
        in_order(root.left)
        print(root.name, end=' ')
        in_order(root.right)


def pre_order(root):
    """
    Pre-order traversal: root -> left -> right
    """
    if root:
        print(root.name, end=' ')
        pre_order(root.left)
        pre_order(root.right)


def post_order(root):
    """
    Post-order traversal: left -> right -> root
    """
    if root:
        post_order(root.left)
        post_order(root.right)
        print(root.name, end=' ')


if __name__ == '__main__':
    # Building the tree structure
    #            A
    #           / \
    #          B   C
    #         / \
    #        D   E
    root = Node('A')
    root.left = Node('B')
    root.right = Node('C')
    root.left.left = Node('D')
    root.left.right = Node('E')

    print('In-order traversal')
    in_order(root)

    print('\n')
    print('Pre-order traversal')
    pre_order(root)

    print('\n')
    print('Post-order traversal')
    post_order(root)
