# source: https://medium.com/@severinperez/maintainable-code-and-the-open-closed-principle-b088c737262
# The code from the source is using JavaScript. Will translate into Python for study purpose here.
#
# Also use the RealPython tutoral on interface to build the meta class interface
# https://realpython.com/python-interface/
# The follow code was originally written in JavaScript but translate it into Python
from abc import ABC, abstractmethod
from random import randint
from typing import List, Union


class MonsterInterface(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def rampage(self, location):
        pass


class Kaiju(MonsterInterface):
    def __init__(self, name):
        self.name = name
        self.type = "Kaiju"

    def rampage(self, location):
        print(f'The {self.type} {self.name} is rampaging through {location}!')


class GreatOldOne(MonsterInterface):
    def __init__(self, name):
        self.name = name
        self.type = "Great Old One"

    def rampage(self, location):
        print(f'The {self.type} {self.name} has awaken from its slumber in {location}!')


class MythicalMonster(MonsterInterface):
    def __init__(self, name):
        self.name = name
        self.type = "Mythical Monster"

    def rampage(self, location):
        print(f'The {self.type} {self.name} has been sighted in {location}!')


class MonsterManager:
    """ Monster Types and Manager """
    def __init__(self, monsters: List[MonsterInterface], locations: List[str]):
        self.monsters = monsters
        self.locations = locations

    def getRandomLocation(self):
        return self.locations[randint(0, len(locations)-1)]

    def rampageAll(self):
        for monster in monsters:
            location = self.getRandomLocation()
            monster.rampage(location)


if __name__ == '__main__':
    """
    The key to open-close principle, in this example, the MonsterManager does not have to change. To create
    a new type of monster, just inherit the MonsterInterface object and create a new monster type. The MonsterManager
    class does not have to change at all
    """
    monsters = []
    locations = ["Athens", "Budapest", "New York", "Santiago", "Tokyo"]

    rodan = Kaiju('Rodan')
    monsters.append(rodan)

    gzxtyos = GreatOldOne('Gzxtyos')
    monsters.append(gzxtyos)

    cerberus = MythicalMonster('Cerberus')
    monsters.append(cerberus)

    myMonsterManager = MonsterManager(monsters, locations)
    myMonsterManager.rampageAll()
