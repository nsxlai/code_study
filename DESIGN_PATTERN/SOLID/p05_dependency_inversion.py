"""
source: https://medium.com/@severinperez/effective-program-structuring-with-the-dependency-inversion-principle-2d5adf11f863

Put concisely, the DIP says that high- and low-level modules should depend on mutual abstractions, and furthermore,
that details should depend on abstractions rather than vice versa.

The original code was written in C#
"""
from abc import ABC, abstractmethod


class ICooker(ABC):
    on = None

    @abstractmethod
    def TurnOn(self):
        pass

    @abstractmethod
    def TurnOff(self):
        pass

    @abstractmethod
    def Cook(self, item: str):
        pass


class Oven(ICooker):
    on = None

    def TurnOn(self):
        print("Turning on the oven!")
        self.on = True

    def TurnOff(self):
        print("Turning off the oven!")
        self.on = False

    def Cook(self, item: str):
        if not self.on:
            print('Oven not turned on.')
        else:
            print(f'Now baking {item}!')


class Stove(ICooker):
    on = None

    def TurnOn(self):
        print("Turning on the stove!")
        self.on = True

    def TurnOff(self):
        print("Turning off the stove!")
        self.on = False

    def Cook(self, item: str):
        if not self.on:
            print('Stove not turned on.')
        else:
            print(f'Now frying {item}!')


class Restaurant:
    def __init__(self, name: str, cooker: ICooker):
        self.name = name
        self.cooker = cooker

    def Cook(self, item: str):
        self.cooker.TurnOn()
        self.cooker.Cook(item)
        self.cooker.TurnOff()


if __name__ == '__main__':
    bakery = Restaurant("Bakery", Oven())
    bakery.Cook("cookies")

    crepery = Restaurant("Crepery", Stove())
    crepery.Cook("crepes")
