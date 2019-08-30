class Node:
    def __init__(self,data):
        self.right=self.left=None
        self.data = data
class Solution:
    def insert(self,root,data):
        if root is None:
            return Node(data)
        else:
            if data<=root.data:
                cur=self.insert(root.left,data)
                root.left=cur
            else:
                cur=self.insert(root.right,data)
                root.right=cur
        return root

    def getHeight(self,root):
        #Write your code here


if __name__ == '__main__':
    # T=int(input())
    # data = int(input())
    data = [3, 5, 2, 1, 4, 6, 7]
    myTree=Solution()
    root=None
    for i in range(len(data)):
        root=myTree.insert(root,data)
    height=myTree.getHeight(root)
    print(height)