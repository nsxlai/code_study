"""
source: https://medium.com/python-features/introduction-to-closures-in-python-8d697ff9e44d

When there are few methods (one method in most cases) to be implemented in a class,
closures can provide an alternate and more elegant solution. Also, closures and nested
functions are especially useful if we want to write code based on the concept of lazy
or delayed evaluation
"""


def countdown(start):
    # This is the outer enclosing function
    def display():
        # This is the nested function
        n = start
        while n > 0:
            n -= 1
            print('T-minus %d' % n)

    return display


if __name__ == '__main__':
    counter1 = countdown(3)
    counter1()
