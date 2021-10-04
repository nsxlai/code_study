"""
source: https://leetcode.com/problems/add-two-numbers/

Problem Statement:
You are given two non-empty linked lists representing two non-negative integers.
The digits are stored in reverse order, and each of their nodes contains a single digit.
Add the two numbers and return the sum as a linked list.

You may assume the two numbers do not contain any leading zero, except the number 0 itself.
Example 1:
Input: l1 = [2,4,3], l2 = [5,6,4]
Output: [7,0,8]
Explanation: 342 + 465 = 807

Example 2:
Input: l1 = [0], l2 = [0]
Output: [0]

Example 3:
Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
Output: [8,9,9,9,0,0,0,1]
"""
from pytest import mark


class ListNode:
    """ Definition for singly-linked list """

    def __init__(self, val: int = 0, next = None):
        self.val = val
        self.next = next


class AddTwoNum:
    def AddTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummyHead = ListNode(0)
        curr = dummyHead
        carry = 0
        while (l1 is not None) or (l2 is not None):  # both lists can be different length. Will pad 0 for missing Node
            x = l1.val if l1 is not None else 0
            y = l2.val if l2 is not None else 0
            sum_val = carry + x + y
            carry = sum_val // 10  # return the floor of the division, integer
            curr.next = ListNode(sum_val % 10)  # Initialize the next node with the carry digit
            curr = curr.next
            if l1 is not None:
                l1 = l1.next
            if l2 is not None:
                l2 = l2.next
        if carry > 0:
            curr.next = ListNode(carry)
        return dummyHead.next


def linked_list(arr: list) -> ListNode:
    hold_list = []

    # Part 1: Add the numbers from the arr to a list of ListNode
    cnt = 0
    while cnt < len(arr):
        hold_list.append(ListNode(arr[cnt]))
        cnt += 1

    # Part 2: Connect each ListNode in the list
    cnt = 0
    while cnt < len(hold_list)-1:  # e.g., 3-element linked list will have 2 connections
        hold_list[cnt].next = hold_list[cnt+1]
        cnt += 1

    return hold_list[0]  # return the first element


test_dict = [([2, 4, 3], [5, 6, 4], [7, 0, 8]),
             ([0], [0], [0]),
             ([9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9], [8, 9, 9, 9, 0, 0, 0, 1]),
             ([3, 6, 9], [7, 5, 3], [0, 2, 3, 1])
             ]


@mark.parametrize('l1, l2, target', test_dict)
def test_base_cases(l1, l2, target):
    l1_linked_list = linked_list(l1)  # Return the first node of the linked list
    l2_linked_list = linked_list(l2)
    target_linked_list = linked_list(target)
    base_node = AddTwoNum()
    result = base_node.AddTwoNumbers(l1_linked_list, l2_linked_list)
    # print(f'{l1 = }, {l2 = }')
    # print(f'{target = }, {result = }')

    while target_linked_list is not None or result is not None:
        if target_linked_list.val != result.val:
            assert False
        if target_linked_list is not None:
            target_linked_list = target_linked_list.next
        if result is not None:
            result = result.next
    assert True
