# source: https://medium.com/analytics-vidhya/metaprogramming-in-python-for-beginners-546adbc76f98


class flag:
    pass


def method_1(self):
    print('this is method 1')


def method_2(self, x):
    return x + 10


def method_3(self):
    return self.y * 10


def mymethod(self):
    return self.x > 100


def method_repr(self):
    print("__repr__ is called")
    return '(repr) NewFlag'


def method_repr1(self):
    print("__repr__ is called")
    return '(repr) NewFlag Updated Method'


def method_str(self):
    print("__str__ is called")
    return '(str) NewFlag'


def method_str1(self):
    print("__str__ is called")
    return '(str) NewFlag Updated Method'


if __name__ == '__main__':
    f = flag()
    print(hasattr(flag, 'flag_method_0'))  # There is no flag_method_1 define at this point (False)
    setattr(flag, 'flag_method_0', lambda self: print('this is flag_method_0'))  # Use lambda function to define class method
    print(hasattr(flag, 'flag_method_0'))
    f.flag_method_0()
    print('-' * 45)
    setattr(flag, 'flag_method_1', method_1)  # Use predefine function and inject it here as a class method
    print(f.flag_method_1())  # Will print the method_1 message and return a None
    f.flag_method_1()  # Will just print the method_1 message
    print('-' * 45)

    setattr(flag, 'flag_method_2', method_2)  # Now add a class method that takes external variables
    flag_var2 = f.flag_method_2(5)
    print(f'flag_var2 = {flag_var2}')
    print('-' * 45)

    setattr(flag, 'y', 20)  # Initialize class attribute y = 20
    setattr(flag, 'flag_method_3', method_3)
    flag_var3 = f.flag_method_3()
    print(f'flag_var3 = {flag_var3}')
    print('-' * 45)

    print('Now building class dynamically')
    class_name = "MyClass"
    base_classes = tuple()
    params = {"x": 10, "check_greater": mymethod}  # Use params dict to define the class attributes and methods
    MyClass = type("MyClass", base_classes, params)
    m = MyClass()
    print(m.check_greater())
    m.x = 200
    print(f'm.x = {m.x}')
    print(m.check_greater())
    print('-' * 45)

    print('Now use flag class as base')
    class_name = 'NewFlag'
    base_class = tuple()
    params = {'y': 20,
              'flag_method_1': method_1,
              'flag_method_2': method_2,
              'flag_method_3': method_3,
              '__repr__': method_repr,
              '__str__': method_str}
    NewFlag = type(class_name, base_class, params)
    nf = NewFlag()
    print(f'nf class = {dir(nf)}')
    nf.flag_method_1()
    print(f'nf.flag_method_2(100) = {nf.flag_method_2(100)}')
    print(f'nf.flag_method_3() = {nf.flag_method_3()}')
    print(f'nf instance repr: {nf!r}')
    print(f'nf instance str: {nf!s}')

    # source: https://medium.com/swlh/string-formatting-in-python-6-things-to-know-about-f-strings-72fd38d96172
    print('\nUpdate __repr__ and __str__ method')
    setattr(nf, '__repr__', method_repr1)
    setattr(nf, '__str__', method_str1)
    print(f'nf instance repr: {nf!r}')
    print(f'nf instance str: {nf!s}')