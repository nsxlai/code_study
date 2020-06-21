# source: http://masnun.rocks/2017/04/15/interfaces-in-python-protocols-and-abcs/

import abc

class Bird(abc.ABC):
    @abc.abstractmethod
    def fly(self):
        pass


class Parrot1(Bird):
    pass


class Parrot2(Bird):
    def fly(self):
        print("Flying")


class Aeroplane(abc.ABC):
    @abc.abstractmethod
    def fly(self):
        pass


class Boeing(Aeroplane):
    def fly(self):
        print("Flying!")


@Bird.register
class Robin:
    pass


if __name__ == '__main__':
    try:
        p = Parrot1()
    except TypeError as te:
        print(te)
        print('Parrot1 did not implement the fly method and it is not allow to instantiate')
        print('because of the rule of the abstract base class (interface)')
        print('This will not be a problem if Bird class is define as regular class ')
        print()
    p = Parrot2()
    print(f'Parrot2 can not be instantiated = {p}')
    print(f'p is a subclass of Bird: {isinstance(p, Bird)}')

    b = Boeing()
    print(f'Parrot is a instance of Aeroplane: {isinstance(p, Aeroplane)}')
    print(f'Bird is a instance of Bird: {isinstance(b, Bird)}')

    r = Robin()
    print('r is Robin class even though Robin did not have the proper method implemented')
    print(f'Robin is a subclass of Bird: {issubclass(Robin, Bird)}')
    print(f'r is a subclass of Bird: {isinstance(r, Bird)}')
    '''
    In this case, even if Robin does not subclass our ABC or define the abstract method, 
    we can register it as a Bird. issubclass and isinstance behavior can be overloaded by 
    adding two relevant magic methods. 
    Read more on that here - https://www.python.org/dev/peps/pep-3119/#overloading-isinstance-and-issubclass
    '''