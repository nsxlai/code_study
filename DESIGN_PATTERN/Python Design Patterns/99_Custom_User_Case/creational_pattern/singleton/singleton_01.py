class Singleton1:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class Singleton2:
    _instance = None

    def __new__(self):
        if not self._instance:
            self._instance = super().__new__(self)
            self.y = 10
        return self._instance


class Borg:
    """Borg pattern making the class attributes global"""
    _shared_data = {}  # Attribute dictionary

    def __init__(self):
        self.__dict__ = self._shared_data  # Make it an attribute dictionary


class Singleton3(Borg):  # Inherits from the Borg class
    """This class now shares all its attributes among its various instances"""

    # This essenstially makes the singleton objects an object-oriented global variable

    def __init__(self, **kwargs):
        # super().__init__()
        Borg().__init__()  # original syntax
        self._shared_data.update(kwargs)  # Update the attribute dictionary by inserting a new key-value pair

    def __str__(self):
        return str(self._shared_data)  # Returns the attribute dictionary for printing


if __name__ == '__main__':
    a = Singleton1()
    b = Singleton1()
    print(f'{a = }')
    print(f'{b = }')
    print(f'{a == b = }')

    print('-' * 40)
    c = Singleton2()
    d = Singleton2()
    print(f'{c = }')
    print(f'{d = }')
    print(f'{c == d = }')

    print(f'{c.y = }')
    print(f'{d.y = }')
    c.y += 20
    print(f'{c.y = }')
    print(f'{d.y = }')

    print('-' * 40)
    e = Singleton3(test01='prog_eeprom')
    f = Singleton3(test02='set_reg')
    print(f'{e = }')
    print(f'{f = }')
    print(f'{e == f = }')
    print(f'{e._shared_data = }, {e}')
    print(f'{f._shared_data = }, {f}')
