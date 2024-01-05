# source: https://levelup.gitconnected.com/writing-a-simple-factory-method-in-python-6e48145d03a

class Bicycle:
    def __init__(self, factory):
        self.tires = factory().add_tires()
        self.frame = factory().add_frame()


class GenericFactory:
    def add_tires(self):
        return GenericTires()

    def add_frame(self):
        return GenericFrame()


class MountainFactory:
    def add_tires(self):
        return RuggedTires()

    def add_frame(self):
        return SturdyFrame()


class RoadFactory:
    def add_tires(self):
        return RoadTires()

    def add_frame(self):
        return LightFrame()


class GenericTires:
    def part_type(self):
        return 'generic_tires'


class RuggedTires:
    def part_type(self):
        return 'rugged_tires'


class RoadTires:
    def part_type(self):
        return 'road_tires'


class GenericFrame:
    def part_type(self):
        return 'generic_frame'


class SturdyFrame:
    def part_type(self):
        return 'sturdy_frame'


class LightFrame:
    def part_type(self):
        return 'light_frame'


if __name__ == '__main__':
    bike = Bicycle(GenericFactory)
    print(bike.tires.part_type())
    print(bike.frame.part_type())

    mountain_bike = Bicycle(MountainFactory)
    print(mountain_bike.tires.part_type())
    print(mountain_bike.frame.part_type())

    road_bike = Bicycle(RoadFactory)
    print(road_bike.tires.part_type())
    print(road_bike.frame.part_type())