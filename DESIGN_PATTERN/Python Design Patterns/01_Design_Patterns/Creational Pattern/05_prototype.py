from copy import deepcopy, copy

copyfunc = deepcopy


def Prototype(name, bases, dict):
    class Cls:
        pass
    Cls.__name__ = name
    Cls.__bases__ = bases
    Cls.__dict__ = dict
    inst = Cls()
    inst.__call__ = copyier(inst)
    return inst


class copyier:
    def __init__(self, inst):
        self._inst = inst

    def __call__(self):
        newinst = copyfunc(self._inst)
        if copyfunc == deepcopy:
            newinst.__call__._inst = newinst
        else:
            newinst.__call__ = copyier(newinst)
        return newinst


class Point:
    __metaclass__ = Prototype
    x = 0
    y = 0

    @classmethod
    def move(cls, x, y):
        cls.x += x
        cls.y += y


if __name__ == '__main__':
    a = Point()
    print(f'a.x = {a.x}, a.y = {a.y}')          # prints 0 0
    a.move(100, 100)
    print(f'a.x = {a.x}, a.y = {a.y}')          # prints 100 100

    Point.move(50, 50)
    print(f'Point.x = {Point.x}, Point.y = {Point.y}')  # prints 50 50

    p = Point()
    print(f'p.x = {p.x}, p.y = {p.y}')          # prints 50 50

    Point.move(200, 200)
    q = Point()
    print(f'q.x = {q.x}, q.y = {q.y}')          # prints 50 50
