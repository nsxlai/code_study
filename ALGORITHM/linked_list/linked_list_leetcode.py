# Definition for singly-linked list.
"""
You are given two non-empty linked lists representing two non-negative integers.
The digits are stored in reverse order and each of their nodes contain a single digit.
Add the two numbers and return it as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.

Example:

Input: (2 -> 4 -> 3) + (5 -> 6 -> 4)
Output: 7 -> 0 -> 8
Explanation: 342 + 465 = 807.
"""
import pdb


class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None


class Solution:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummyHead = ListNode(0)
        curr = dummyHead
        carry = 0
        while (l1 != None) or (l2 != None):  # both lists can be different length. Will pad 0 for missing Node
            x = l1.val if l1 != None else 0
            y = l2.val if l2 != None else 0
            sum_val = carry + x + y
            carry = int(sum_val / 10)
            curr.next = ListNode(sum_val % 10)
            curr = curr.next
            if (l1 != None):
                l1 = l1.next
            if (l2 != None):
                l2 = l2.next
        if (carry > 0):
            curr.next = ListNode(carry)
        return dummyHead.next


if __name__ == '__main__':
    l1 = ListNode(2)
    b1 = ListNode(4)
    c1 = ListNode(3)
    l1.next = b1
    b1.next = c1

    l2 = ListNode(5)
    b2 = ListNode(6)
    c2 = ListNode(4)
    l2.next = b2
    b2.next = c2

    a = Solution()
    result = a.addTwoNumbers(l1, l2)
    curr = result
    for i in range(3):
        print(result.val)
        result = result.next
