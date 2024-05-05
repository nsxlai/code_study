"""
source: Medium article "3 Levels of Understanding the Singleton Pattern in Python"

Comment structure source: https://medium.com/python-features/instance-creation-in-python-9268d320f0a
We haven’t defined dunder new in our Employee class but we do inherit an implementation from the universal
base class object. So it is the base class implementation of dunder new which is responsible for allocating
our object in this case.

Hence, inherited __new__() allocates the object which is passed to the __init__() constructor as self.
Now, let’s try to override dunder new method to understand its signature better. We’ll implement the most
basic override of dunder new, which simply delegates to base class implementation, along with adding few
print statements, to inspect the arguments and return value.

The first thing to note is, dunder new is a class method. It expects cls as its first argument rather than
self. The cls argument is the class of the new object, which will be allocated. In addition, dunder new
accepts whatever parameters have been passed to the constructor. In this case, we have used the *args and **kwargs
for the same.

The main purpose of dunder new is to allocate the instance of the calling class. All object
allocation must be done by the dunder new implementation on the ultimate base class object. We’ve used super()
to refer the object new method since that is more maintainable. (if ultimate base class object changes in future).
Finally, we are returning the newly created object obj which is passed to the __init__ method as self. This can
be confirmed by comparing the ids of both objects.

Summary:
1. dunder new __new__() allocates and returns new instances. It is an implicit class method that accepts
class of the new instance as its first argument.
2. object.__new__() is the ultimate allocator which allocates all instances.
3. dunder init __init__ is responsible for mutating the instance it has been given.
"""


class Singleton:
    __instance = None  # double underscore (__) will put the attribute as "private" in Python

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)  # can also replace "object" with "super()", like in singleton_01
        return cls.__instance

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


if __name__ == '__main__':
    s1 = Singleton("Mary", "Maryville")
    s2 = Singleton("Fred", "Fedrick")

    print(s1)
    print(s2)
    print(s1 == s2)

    print(s1.last_name)
    print(s2.last_name)


