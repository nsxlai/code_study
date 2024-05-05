"""
source: https://medium.com/@apps.merkurev/dont-forget-about-slots-in-python-c397f414c490

When __slots__ is defined, Python uses an alternative storage model for instance attributes:
the attributes are stored in a hidden array of references, which consumes significantly less memory than a dictionary.

The __slots__ attribute itself is a sequence of the instance attribute names.
It must be present at the time of class declaration; adding or modifying it later has no effect.

The benefits of using __slots__ over the traditional __dict__? There are three main aspects:
1. Faster access to instance attributes
2. Memory savings
3. More secure access to instance attributes

----------------------------------------------------------------------------------------------------------------
source: https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
Bytes  type        scaling notes
28     int         +4 bytes about every 30 powers of 2
37     bytes       +1 byte per additional byte
49     str         +1-4 per additional character (depending on max width)
48     tuple       +8 per additional item
64     list        +8 for each additional
224    set         5th increases to 736; 21nd, 2272; 85th, 8416; 341, 32992
240    dict        6th increases to 368; 22nd, 1184; 43rd, 2280; 86th, 4704; 171st, 9320
136    func def    does not include default args and other attrs
1056   class def   no slots
56     class inst  has a __dict__ attr, same scaling as dict above
888    class def   with slots
16     __slots__   seems to store in mutable tuple-like structure
                   first slot grows to 48, and so on.

----------------------------------------------------------------------------------------------------------------
Use Pympler to get the true size of the Python object: https://pypi.org/project/Pympler/
Pympler is a development tool to measure, monitor and analyze the memory behavior of Python objects
in a running Python application.
"""
import datetime
from pympler import asizeof
import sys
from timeit import timeit


class Book0:
    """
    Example 0 class
    """
    __slots__ = ('title', 'author', 'isbn', 'pub_date', 'rating')


class Point:
    """
    Example 2: __dict__
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def point_def(self):
        print(f'Coordinate: ({self.x}, {self.y})')


class SlotPoint:
    """
    Example 2: __slots__
    """
    __slots__ = ('x', 'y')

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def point_def(self):
        print(f'Coordinate: ({self.x}, {self.y})')


class Book3:
    pass


class SlotBook3:
    __slots__ = ()


def example_00():
    """
    This example shows the __dict__ and __slot operation.
    """
    book = Book0()
    book.title = 'Learning Python'
    book.author = 'Mark Lutz'
    book.pub_date = datetime.date(2013, 7, 30)
    book.rating = 4.98

    print(f'Show newly updated title attribute: {book.title = }')  # Learning Python
    print(f'Show newly updated rating attribute: {book.rating = }')  # 4.98

    # This will raise AttributeError: 'Book' object has no attribute '__dict__'
    try:
        print(f'Show the __dict__ attribute: {book.__dict__ = }')
    except AttributeError as e:
        print(e)


def example_01():
    """
    This example shows the time performance of the __dict__ and __slots__ objects
    """
    def point_func():
        return [Point(n, n + 1) for n in range(1000)]

    def slot_point_func():
        return [SlotPoint(n, n + 1) for n in range(1000)]

    p_dict_time = timeit(stmt=point_func, number=10_000)
    print(f'List of 10,000 classes with dict: {p_dict_time}')

    p_slot_time = timeit(stmt=slot_point_func, number=10_000)
    print(f'List of 10,000 classes with slot: {p_slot_time}')


def example_02():
    """
    This example shows the size of the __dict__ and __slots__ objects
    """
    p_dict = [Point(n, n + 1) for n in range(1000)]
    print(f'Point (__dict__; pympler): {asizeof.asizeof(p_dict)} bytes')  # Point: 216768 bytes
    print(f'Point (__dict__; sys):     {sys.getsizeof(p_dict)} bytes')

    p_slot = [SlotPoint(n, n + 1) for n in range(1000)]
    print(f'SlotPoint (__slot__; pympler): {asizeof.asizeof(p_slot)} bytes')  # SlotPoint: 112656 bytes
    print(f'SlotPoint (__slot__; sys):     {sys.getsizeof(p_slot)} bytes')


def example_03():
    """
    This example shows the attribute access (security)
    """
    book31 = Book3()
    book31.title = 'Learning Python'  # no error, a new attribute is created
    print(f'Show newly updated title attribute: {book31.title = }')  # Learning Python

    book32 = SlotBook3()

    # This will raise AttributeError: 'SlotBook' object has no attribute 'title'
    try:
        book32.title = 'Learning Python'
    except AttributeError as e:
        print(e)


if __name__ == '__main__':

    print(' Example 00 '.center(60, '='))
    example_00()

    print(' Example 01 '.center(60, '='))
    example_01()

    print(' Example 02 '.center(60, '='))
    example_02()

    print(' Example 03 '.center(60, '='))
    example_03()
