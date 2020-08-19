"""
Reference: https://www.geeksforgeeks.org/stack-in-python/

Stack is a LIFO data structure and it has follow methods associated with it:
    empty() – Returns whether the stack is empty – Time Complexity : O(1)
    size() – Returns the size of the stack – Time Complexity : O(1)
    top() – Returns a reference to the top most element of the stack – Time Complexity : O(1)
    push(g) – Adds the element ‘g’ at the top of the stack – Time Complexity : O(1)
    pop() – Deletes the top most element of the stack – Time Complexity : O(1)

    Initialize the Stack data structure with 'maxsize' parameter to determine the maximum size of Stack
"""
from random import randint
from typing import Union


class Stack:
    """ Use the List data structure to create the custom stack data structure """
    def __init__(self, maxsize: int = 5):
        self.data = []
        self.maxsize = maxsize

    def __repr__(self) -> str:
        return f'len = {len(self.data)}; Stack({self.data})'

    def is_empty(self) -> bool:
        if len(self.data) > 0:
            return False
        return True

    def is_full(self) -> bool:
        if len(self.data) >= self.maxsize:
            return True
        return False

    def size(self) -> int:
        return len(self.data)

    def top(self) -> Union[int, None]:
        if self.is_empty():
            print(f'Stack is empty')
            return None
        return self.data[-1]

    def push(self, data) -> None:
        if self.is_full():
            print(f'Unable to push new data; Stack is full')
        else:
            self.data.append(data)

    def pop(self) -> Union[int, None]:
        if self.is_empty():
            print(f'Unable to pop; Stack is empty')
            return None
        return self.data.pop()


def init_stack(stack_size: int) -> Stack:
    mstack = Stack(maxsize=stack_size)
    for i in range(stack_size):
        mstack.push(randint(0, 100))  # insert a random value from 0 to 100
    print(mstack)
    return mstack


if __name__ == '__main__':
    my_stack = init_stack(10)

    print(f'Stack is full? {my_stack.is_full()}')
    my_stack.push(10)
    print(my_stack)

    print('Popping stack...')
    for _ in range(9):
        my_stack.pop()
        print(my_stack)

    top_value = my_stack.top()
    print(f'top_value = {top_value}')
    value = my_stack.pop()
    print(f'Last element to pop: {value}')
    print(my_stack)
    my_stack.pop()
    my_stack.push(25)
    my_stack.push(50)
    print(my_stack)
    print(f'my_stack.size = {my_stack.size()}')

