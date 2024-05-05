"""
source: https://medium.com/@aditi-mishra/singleton-pattern-in-python-libraries-8509903fb474

1. Using a decorator to implement the singleton pattern
"""


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class MyClass:
    pass


if __name__ == '__main__':
    c1 = MyClass()
    c2 = MyClass()

    print(f'{id(c1) = }')
    print(f'{id(c2) = }')

    if id(c1) == id(c2):
        print('c1 object is the same object as c2')
