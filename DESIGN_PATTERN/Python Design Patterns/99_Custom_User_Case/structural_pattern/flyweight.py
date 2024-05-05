"""
source: https://towardsdev.com/design-patterns-in-python-flyweight-pattern-ec3d321a86af

Flyweight Design Pattern can be used to prevent the uncontrolled increase in the number
of objects and to ensure that the objects are used repeatedly.

A flyweight object can be used jointly in different environments and can adapt to the
environment. For example, a car object may look in different colors in different
environments (states), only the image (color, etc) changes, and the object is the same.
Rather than creating a new car object from scratch, it may be more logical to take and
replace the same object in a new environment. Such situations are called extrinsic states,
this is dependent on external conditions, that is, the presence of the same type of object
in different states. An intrinsic state is an actual state which is represented by the
Flyweight object.
"""


class Cat:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
        self.sound = "Meow"


class CatExt:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z


class CatArmyFly:
    def __init__(self):
        self.sound = "Meow"
        self.cat_soldiers = []

    def cat_factory(self, x: int, y: int, z: int):
        _list = []

        # Check if the Cat signature is already in the CAT soldiers list
        for cs in self.cat_soldiers:
            if cs.x == x and cs.y == y and cs.z == z:
                _list.append(cs)
        if not _list:
            _list = Cat(x, y, z)
            self.cat_soldiers.append(_list)
        else:
            _list = _list[0]
        return _list

    def get_cats(self):
        print("Cats: ")
        for cat in self.cat_soldiers:
            print(str(cat.x) + " " + str(cat.y) + " " + str(cat.z) + " " + cat.sound)


if __name__ == '__main__':
    fly = CatArmyFly()
    fly.cat_factory(3, 4, 5)
    fly.cat_factory(1, 0, 0)
    fly.cat_factory(3, 4, 5)
    fly.cat_factory(7, 8, 9)
    fly.get_cats()
    fly.cat_soldiers
