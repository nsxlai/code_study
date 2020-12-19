# source: https://medium.com/better-programming/abstract-classes-and-metaclasses-in-python-9236ccfbf88b
from abc import ABC, abstractmethod


class AbstractVehicle(ABC):
    @property
    @abstractmethod
    def engine(self):
        raise NotImplementedError()

    @engine.setter
    @abstractmethod
    def engine(self, _engine):
        raise NotImplementedError()


class Car(AbstractVehicle):
    _engine = ''

    @property
    def engine(self):
        return self._engine

    @engine.setter
    def engine(self, new_engine):
        self._engine = new_engine.upper()


if __name__ == '__main__':
    car = Car()
    car.engine = 'v8 3.2 liters'
    print(car.engine)
