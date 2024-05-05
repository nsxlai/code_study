# https://www.geeksforgeeks.org/private-methods-in-python/
class Base:

    # Declaring public method
    def fun(self):
        print("Public method")

    # Declaring private method
    def __fun(self):
        print("Private method")


class Derived(Base):
    def __init__(self):
        # Calling constructor of
        # Base class
        Base.__init__(self)

    def call_public(self):
        # Calling public method of base class
        print("\nInside derived class")
        self.fun()

    def call_private(self):
        # Calling private method of base class
        self.__fun()


if __name__ == '__main__':
    # Driver code
    obj1 = Base()

    # Calling public method
    obj1.fun()

    obj2 = Derived()
    obj2.call_public()

    # Uncommenting obj1.__fun() will
    # raise an AttributeError
    try:
        obj1.__fun()
    except AttributeError as e:
        print(e)
        print('AttributeError for calling obj1.__fun()')

    # Uncommenting obj2.call_private()
    # will also raise an AttributeError
    try:
        obj2.call_private()
    except AttributeError as e:
        print(e)
        print('AttributeError for calling obj2.call_private()')
