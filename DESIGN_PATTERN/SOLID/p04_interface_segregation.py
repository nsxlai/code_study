"""
source: https://medium.com/@severinperez/avoiding-interface-pollution-with-the-interface-segregation-principle-5d3859c21013

Because an interface is a contract, you would be forced to define behaviors that are effectively useless.
This is known colloquially as “interface pollution” because a class may become polluted with behaviors that
it doesn’t need. interface pollution was primarily the result of “fat interfaces” — that is, interfaces with
a large number of prescribed methods. Clients should not be forced to depend upon interfaces that they do not use.
The original code was written in C#
"""
from abc import ABC, abstractmethod
import math


class IArithmetic(ABC):
    @abstractmethod
    def add(self, num1: int, num2: int):
        pass

    @abstractmethod
    def subtract(self, num1: int, num2: int):
        pass

    @abstractmethod
    def multiply(self, num1: int, num2: int):
        pass

    @abstractmethod
    def divide(self, num1: int, num2: int):
        pass


class IExponents(ABC):
    def power(self, num: int, power: int):
        pass

    def square_root(self, num: int):
        pass


class BasicCalculator(IArithmetic):
    def add(self, num1: int, num2: int) -> int:
        return num1 + num2

    def subtract(self, num1: int, num2: int) -> int:
        return num1 - num2

    def multiply(self, num1: int, num2: int) -> int:
        return num1 * num2;

    def divide(self, num1: int, num2: int) -> float:
        return num1 / num2


class AdvancedCalculator(IArithmetic, IExponents):
    def add(self, num1: int, num2: int) -> int:
        return num1 + num2

    def subtract(self, num1: int, num2: int) -> int:
        return num1 - num2

    def multiply(self, num1: int, num2: int) -> int:
        return num1 * num2

    def divide(self, num1: int, num2: int) -> float:
        return num1 / num2

    def power(self, num: int, power: int) -> float:
        return math.pow(num, power)

    def square_root(self, num: int) -> float:
        return math.sqrt(num)


if __name__ == '__main__':
    basic_calc = BasicCalculator()
    adv_calc = AdvancedCalculator()

    print(f'Basic calculator: 3 + 5 = {basic_calc.add(3, 5)}')
    print(f'Basic calculator: 10 - 3.5 = {basic_calc.subtract(10, 3)}')
    print(f'Basic calculator: 6 * 7 = {basic_calc.multiply(6, 7)}')
    print(f'Basic calculator: 20 / 4 = {basic_calc.add(20, 4)}')

    print(f'Advance calculator: 3^5 = {adv_calc.power(3, 5)}')
    print(f'Advance calculator: Sqare root of 3 = {adv_calc.square_root(3):.3f}')
