"""
source: https://python.plainenglish.io/design-patterns-in-python-prototype-pattern-9e520d36565e
"""
import time
import copy
from abc import ABC, abstractmethod


class StModel21:
    def __init__(self, model_year: int, attack_power: float, defence_power: float, cpu_type: str):
        # an expensive object creation process
        print('Creating ST in progress (5 seconds)...')
        time.sleep(5)
        # attributes
        self.model_year = model_year
        self.attack_power = attack_power
        self.defence_power = defence_power
        self.cpu_type = cpu_type
        print('Creation completed...')


class Prototype(ABC):
    def __init__(self, model_year: int, attack_power: float, defence_power: float, cpu_type: str):
        # an expensive object creation process
        print('Creating ST in progress (7 seconds)...')
        time.sleep(7)
        # attributes
        self.model_year = model_year
        self.attack_power = attack_power
        self.defence_power = defence_power
        self.cpu_type = cpu_type
        print('Creation completed...')

    @abstractmethod
    def clone(self):
        pass


class StModel22(Prototype):
    def __init__(self, model_year, attack_power, defence_power, cpu_type):
        super().__init__(model_year, attack_power, defence_power, cpu_type)

    def clone(self):
        return copy.deepcopy(self)


if __name__ == '__main__':
    # First instantiate StModel20 (old model); there is a 30 second cost to create each object
    ST_21_1 = StModel21(model_year=2021, attack_power=2, defence_power=2, cpu_type='csad2')
    ST_21_2 = StModel21(model_year=2021, attack_power=2, defence_power=2, cpu_type='csad2')

    # Check the ST status:
    print(f'{repr(ST_21_1) = }, {id(ST_21_1) = }')
    print(f'{repr(ST_21_2) = }, {id(ST_21_2) = }')
    print()

    # Each ST creation takes a while. Creating a whole army will take a very long time.
    # Consider cloning with the prototype pattern
    ST_22_1 = StModel22(model_year=2022, attack_power=3, defence_power=2, cpu_type='csad2')
    ST_22_2 = StModel22.clone(ST_22_1)
    ST_22_3 = StModel22.clone(ST_22_1)
    ST_22_4 = StModel22.clone(ST_22_1)

    # Only the initial ST takes the time to create. The rest of the ST didn't take the same creation time
    print(f'{repr(ST_22_1) = }, {id(ST_22_1) = }')
    print(f'{repr(ST_22_2) = }, {id(ST_22_2) = }')
    print(f'{repr(ST_22_3) = }, {id(ST_22_3) = }')
    print(f'{repr(ST_22_4) = }, {id(ST_22_4) = }')
    print()

    # Alter the characteristic of some ST
    print(f'{ST_22_3.__dict__ = }')
    ST_22_3.cpu_type = 'csad3'
    ST_22_3.attack_power = 5

    print(f'{repr(ST_22_1) = }, {id(ST_22_1) = }')
    print(f'{repr(ST_22_2) = }, {id(ST_22_2) = }')
    print(f'{repr(ST_22_3) = }, {id(ST_22_3) = }')
    print(f'{repr(ST_22_4) = }, {id(ST_22_4) = }')

    # The attribute of the ST is changed but the object stayed at the same ID
    print(f'{ST_22_3.__dict__ = }')
    print()

    # Clone the new ST with the updated ST_22_3 attributes
    ST_22_5 = ST_22_3.clone()
    print(f'{repr(ST_22_5) = }, {id(ST_22_5) = }')
    print(f'{ST_22_5.__dict__ = }')
