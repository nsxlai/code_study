"""
source: https://medium.com/@aditi-mishra/singleton-pattern-in-python-libraries-8509903fb474

3. Using metaclass to implement the singleton pattern
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MyClass(metaclass=Singleton):
    pass


if __name__ == '__main__':
    f1 = MyClass()
    f2 = MyClass()

    print(f'{id(f1) = }')
    print(f'{id(f2) = }')

    if id(f1) == id(f2):
        print('f1 object is the same object as f2')
