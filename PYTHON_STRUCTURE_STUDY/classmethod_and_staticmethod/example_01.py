# source:

from datetime import date


class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    @staticmethod
    def fromFathersAge(name, fatherAge, fatherPersonAgeDiff):
        return Person(name, date.today().year - fatherAge + fatherPersonAgeDiff)

    @classmethod
    def fromBirthYear(cls, name, birthYear):
        return cls(name, date.today().year - birthYear)

    def display(self):
        print(self.name + "'s age is: " + str(self.age))


class Man(Person):
    sex = 'Male'


if __name__ == '__main__':
    man = Man.fromBirthYear('John', 1985)
    print(f'{isinstance(man, Man) = }')
    print(f'{man.display() = }')

    man1 = Man.fromFathersAge('John', 1965, 20)
    print(f'{isinstance(man1, Man)}')
    print(f'{man1.display = }')