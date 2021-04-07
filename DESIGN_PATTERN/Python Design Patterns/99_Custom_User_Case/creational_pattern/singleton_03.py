# source: Medium article "3 Levels of Understanding the Singleton Pattern in Python"

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


