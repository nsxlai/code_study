from abc import ABC, abstractmethod
import math


class calc01(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def substract(self):
        pass

    @abstractmethod
    def multiply(self):
        pass

    @abstractmethod
    def divide(self):
        pass


class calc02(ABC):
    @abstractmethod
    def pow(self):
        pass

    @abstractmethod
    def sqrt(self):
        pass


class basicCalc_bad(calc01):
    def add(self, x, y):
        return x + y
    
    def substract(self, x, y):
        return x - y
    
    def multiply(self, x, y):
        return x * y


class basicCalc_good(calc01):
    def add(self, x, y):
        return x + y
    
    def substract(self, x, y):
        return x - y
    
    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        return x / y


class advanceCalc(calc01, calc02):
    def add(self, x, y):
        return x + y
    
    def substract(self, x, y):
        return x - y
    
    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        return x / y
    
    def pow(self, x, y):
        return int(math.pow(x, y))

    def sqrt(self, x):
        return math.sqrt(x)

if __name__ == '__main__':
    try:
        basic = basicCalc_bad()
        print(f'basic Calc 3 + 4: {basic.add(3, 4)}')
    except TypeError as e:
        print('Unable to instantiate basicCalc_bad class')
        print(e)
    
    print('-' * 25)
    basic = basicCalc_good()
    print(f'basic Calc 3 + 4 = {basic.add(3, 4)}')
    print(f'basic Calc 3 / 4 = {basic.divide(3, 4)}')

    print('-' * 25)
    adv = advanceCalc()  # Takes 2 role interfaces to construct the concrete class
    print(f'adv Calc 2^3 = {adv.pow(2, 3)}')
    print(f'adv Calc sqrt(5) = {adv.sqrt(5):5.3f}')
