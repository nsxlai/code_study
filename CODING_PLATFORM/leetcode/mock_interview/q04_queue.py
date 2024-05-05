from collections import deque


class MyQueue:
    def __doc__(self):
        """
        push method will add the element to the end of the queue
        pop method will add the element to the beginning of the queue
        peek method will return the first element of the queue
        empty method will check if the queue is empty
        :return:
        """
    def __init__(self):
        self.queue = deque()

    def push(self, x: int) -> None:
        self.queue.append(x)

    def pop(self) -> int:
        return self.queue.popleft()

    def peek(self) -> int:
        return self.queue[0]

    def empty(self) -> bool:
        if len(self.queue) > 0:
            return False
        return True


if __name__ == '__main__':
    # Your MyQueue object will be instantiated and called as such:
    # ["MyQueue", "push", "push", "peek", "pop", "empty"]
    # [       [],    [1],    [2],     [],    [],      []]
    # [     null,   null,   null,      1,     2,   false]

    obj = MyQueue()
    obj.push(1)
    obj.push(2)
    print(f'peek: {obj.peek()}')
    print(f'pop : {obj.pop()}')
    print(f'empty?: {obj.empty()}')
    print(dir(obj))
