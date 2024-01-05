f"""
source: https://medium.com/@shanenullain/abstract-factory-in-python-with-generic-typing-b9ceca2bf89e
"""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Dict, Type


class Player(ABC):
    @abstractmethod
    def attack(self, damage: int) -> bool:
        pass


class Rogue(Player):
    def attack(self, damage: int) -> bool:
        MINIMUM_DAMAGE_TO_HIT: int = 5
        return damage > MINIMUM_DAMAGE_TO_HIT


class Item(ABC):
    @abstractmethod
    def get_damage(self) -> int:
        pass


class Sword(Item):
    def get_damage(self) -> int:
        return 10


T = TypeVar('T')


class AbstractEntityFactory(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: str) -> T:
        pass


class ItemFactory(AbstractEntityFactory[Item]):

    _items: Dict[str, Type[Item]] = {'sword': Sword}

    def create(self, entity: str) -> Item:
        if entity in self._items:
            return self._items[entity]()

        raise KeyError(entity)


class PlayerFactory(AbstractEntityFactory[Player]):

    _players: Dict[str, Type[Player]] = {'rogue': Rogue}

    def create(self, entity: str) -> Player:
        if entity in self._players:
            return self._players[entity]()

        raise KeyError(entity)


class GameFactory:

    _factories: Dict[str, Type[AbstractEntityFactory]] = {'player': PlayerFactory,
                                                          'item': ItemFactory}

    @classmethod
    def get_factory(cls, factory: str) -> AbstractEntityFactory:
        if factory in cls._factories:
            return cls._factories[factory]()

        raise KeyError(factory)


if __name__ == '__main__':
    item_factory: AbstractEntityFactory = GameFactory.get_factory('item')
    item_sword: Item = item_factory.create('sword')
    item_sword.get_damage()  # returns 10

    player_factory: AbstractEntityFactory = GameFactory.get_factory('player')
    rogue: Player = player_factory.create('rogue')
    rogue.attack(1)  # returns False
    rogue.attack(item_sword.get_damage())  # returns True
