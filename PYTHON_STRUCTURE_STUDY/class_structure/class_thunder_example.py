"""
source: https://python.plainenglish.io/you-dont-know-python-if-you-don-t-know-these-dunder-methods-3ed52ee9e7a0
source: https://realpython.com/python-super/
"""


class Rectangle:
    def __init__(self, width: int, length: int):
        self.width = width
        self.length = length

    def area(self):
        return self.width * self.length

    def perimeter(self):
        return 2 * self.length + 2 * self.width

    def __str__(self):
        return 'Finding the area and perimeter of Rectangle'

    def __repr__(self):
        """
        the eval of the __repr__ representation is the object itself:
        eval(repr(Rectangle)) = Rectangle

        For more than 2 variables, a tuple bracket is added automatically.
        Compare to the Square with 1 variable (bracket around the variable).
        """
        return f'Rectangle{self.width, self.length}'

    def __eq__(self, other):
        if type(self) != type(other):  # if the object types are different, return False
            return False
        return all([
            self.length == other.length,
            self.width == other.width
        ])

    def __ne__(self, other):
        """ return the opposite of __eq__ method, require __eq__ to be implemented first """
        return not self == other

    def __lt__(self, other):
        if type(self) != type(other):  # if the object types are difference, raise exception_with_test
            raise TypeError('Self and other must be instances of the same class')
        return self.length < other.length  # use length as the main comparison attribute

    def __le__(self, other):
        """ Less than or equal to, need to implement __eq__ and __lt__ first """
        return self == other or self < other

    def __gt__(self, other):
        """ Need to implement __eq__, __lt__, and __le__ first """
        return not self <= other

    def __ge__(self, other):
        return self > other or self == other

    def __add__(self, other):
        return self.area() + other.area()


class Square(Rectangle):
    def __init__(self, side: int):
        super().__init__(side, side)
        self.side = side

    def __str__(self):
        return 'Finding the area and perimeter of Square'

    def __repr__(self):
        """
        the eval of the __repr__ representation is the object itself:
        eval(repr(Square)) = Square
        """
        return f'Square({self.side})'


if __name__ == '__main__':
    rectangle = Rectangle(3, 4)
    square = Square(3)
    print(f'{rectangle = }')  # uses __repr__
    print(f'{square = }')
    print(f'{rectangle.perimeter() = }')  # uses __repr__
    print(f'{square.area() = }')
    print(f'{repr(rectangle) = }')
    print(f'{repr(square) = }')
    print(f'{eval(repr(rectangle)) = }')
    print(f'{eval(repr(square)) = }')
    print(f'Rectangle instance repr: {rectangle!r}')
    print(f'Rectangle instance str: {rectangle!s}')
    print(f'Square instance repr: {square!r}')
    print(f'Square instance str: {square!s}')

    sq1 = Square(5)
    sq2 = Square(5)
    sq3 = Square(10)
    print(f'{sq1 == sq2 = }')  # if the __eq__ is not implemented, this will be False
    print(f'{sq1.__eq__(sq2) = }')
    print(f'{sq1.__ne__(sq3) = }')

    print(f'{sq1 < sq3 = }')
    print(f'{sq1 < sq2 = }')  # same as sq1.__lt__(sq2)
    print(f'{sq1 <= sq2 = }')  # same as sq1.__le__(sq2)

    print('-' * 40)
    print(f'{sq1.__add__(sq2) = }')
    print(f'{sq1 + sq3 = }')
    print(f'{sq3 + sq1 = }')
