# source: https://medium.com/better-programming/decorators-in-python-72a1d578eac4

class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        """Get value of radius"""
        return self._radius

    @radius.setter
    def radius(self, value):
        """Set radius, raise error if negative
           .radius is now mutable because of the .setter() method
        """
        if value >= 0:
            self._radius = value
        else:
            raise ValueError("Radius must be positive")

    @property
    def area(self):
        """
        Calculate area inside circle
        Area is immutable; it has property without .setter() method so its value cannot be changed
        """
        return self.pi() * self.radius**2

    def cylinder_volume(self, height):
        """Calculate volume of cylinder with circle as base"""
        return self.area * height

    @classmethod
    def unit_circle(cls):
        """Factory method creating a circle with radius 1"""
        return cls(1)

    @staticmethod
    def pi():
        """Value of π, could use math.pi instead though
           Static method can be called on either an instance or the class
        """
        return 3.1415926535


if __name__ == '__main__':
    c = Circle(5)
    print(f'{c.radius = }')
    print(f'{c.area = }')
    c.radius = 2
    print(f'{c.area = }')

    try:
        c.area = 100
    except AttributeError as e:
        print(e)

    c.cylinder_volume(height=4)

    try:
        c.radius = -1
    except ValueError as e:
        print(e)

    c1 = Circle.unit_circle()
    print(f'{c1.radius = }')
    print(f'{c.pi() = }')
    print(f'{Circle.pi() = }')
