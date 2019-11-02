def debug_function(func):
    def wrapper(*args, **kwargs):
        print(f'{func.__qualname__} is called with parameter {args[1:]}')
        return func(*args, **kwargs)
    return wrapper


def debug_all_methods(cls):
    for key, val in vars(cls).items():
        if callable(val):
            setattr(cls, key, debug_function(val))
    return cls


class MetaClassDebug(type):
    def __new__(cls, clsname, bases, clsdict):
        obj = super().__new__(cls, clsname, bases, clsdict)
        obj = debug_all_methods(obj)
        return obj


class Calc(metaclass=MetaClassDebug):
    def add(self, x, y):
        return x + y

    def sub(self, x, y):
        return x - y

    def mul(self, x, y):
        return x * y


if __name__ == '__main__':
    calc = Calc()
    print(calc.add(2, 3))
    print(calc.sub(2, 3))
    print(calc.mul(2, 3))
