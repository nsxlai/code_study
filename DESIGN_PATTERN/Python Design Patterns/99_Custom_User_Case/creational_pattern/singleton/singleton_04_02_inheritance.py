"""
source: https://medium.com/@aditi-mishra/singleton-pattern-in-python-libraries-8509903fb474

2. Using inheritance to implement the singleton pattern
"""


class Singleton:
    _instance = None

    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance


class MyClass(Singleton):
    pass


if __name__ == '__main__':
    d1 = MyClass()
    d2 = MyClass()

    print(f'{id(d1) = }')
    print(f'{id(d2) = }')

    if id(d1) == id(d2):
        print('d1 object is the same object as d2')
