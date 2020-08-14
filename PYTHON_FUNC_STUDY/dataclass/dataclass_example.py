# source: https://towardsdatascience.com/data-classes-in-python-8d1a09c1294b
# Data class are available for Python 3.7 and above
from dataclasses import dataclass, field, asdict, astuple


@dataclass
class Coordinate:
    x: int
    y: int
    z: int


@dataclass
class CircleArea:
    r: int
    pi: float = 3.14

    @property
    def area(self):
        return self.pi * (self.r ** 2)


@dataclass(frozen=True)
class CircleArea2:
    '''data will be immutable when declare frozen=True'''
    r: int
    pi: float = 3.14

    @property
    def area(self):
        return self.pi * (self.r ** 2)


@dataclass(order=True)
class Vector:
    """
    By default, order parameter of data class is False.
    When you set it to True; __lt__, __le__,__gt__ and __ge__ methods
    will be automagically generated for your data class.
    So you can make comparison of objects as if they were tuples of
    their fields in order.
    """
    magnitude: float = field(init=False)
    x: int
    y: int

    def __post_init__(self):
        self.magnitude = (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass
class Vector2:
    x: int
    y: int
    z: int


@dataclass
class Employee:
    name: str
    lang: str


@dataclass
class Developer(Employee):
    """ Inheritance """
    salary: int


@dataclass
class Employee2:
    ''' Use Slot instead of dict reduces memory usage '''
    __slots__ = ('name', 'lang')
    name: str
    lang: str


if __name__ == '__main__':
    a = Coordinate(3, 4, 5)
    print(a)  # __repr__ is implemented

    b = CircleArea(2)
    print(repr(b))
    print(f'Area = {b.area}')

    c = CircleArea2(5)
    # c.r = 5  # will get the error message: dataclasses.FrozenInstanceError: cannot assign to field 'r'

    v1 = Vector(8, 15)
    v2 = Vector(7, 20)
    print(f'{v2 > v1 = }')

    v1 = Vector(9, 12)
    print(f'{v1=}')  # output: Vector(magnitude=15.0, x=9, y=12)
    v2 = Vector(8, 15)
    print(f'{v2=}')  # output: Vector(magnitude=17.0, x=8, y=15)
    print(f'{v2 > v1 = }')  # output: True

    v = Vector2(4, 5, 7)
    print(asdict(v))  # output: {'x': 4, 'y': 5, 'z': 7}
    print(astuple(v))  # output: (4, 5, 7)

    h = Developer('Hello', 'Python', 5000)
    print(f'{h=}')  # Output: Developer(name='Hello', lang='Python', salary=5000)

    h2 = Employee('Hello2', 'Python')
    print(f'{h2=}')