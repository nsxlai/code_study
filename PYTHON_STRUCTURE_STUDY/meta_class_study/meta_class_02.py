# source: https://medium.com/analytics-vidhya/metaprogramming-in-python-for-beginners-546adbc76f98

class flag:
    pass


def method_1(self, x):
    return self.x > 100

def method_2(self):
    print('this is method 2')


class_name = "MyClass"
base_classes = tuple()
params= {"x": 10, "check_greater": mymethod}
MyClass = type("MyClass", base_classes, params)
obj = MyClass()
print(obj.check_greater())


if __name__ == '__main__':
    f = flag()
    print(hasattr(flag, 'attr_a'))
    setattr(flag, 'attr_a', lambda: print('this is attr_a'))
    print(hasattr(flag, 'attr_a'))
    f.attr_a()
    setattr(flag, 'flag_method_2', method_2)
    print(f.attr_b())