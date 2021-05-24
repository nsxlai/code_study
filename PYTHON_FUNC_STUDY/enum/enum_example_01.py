"""
source: https://betterprogramming.pub/take-advantage-of-the-enum-class-to-implement-enumerations-in-python-1b65b530e1d
source: https://towardsdatascience.com/how-to-make-fewer-mistakes-in-python-6925619ce87e
"""
from enum import Enum
from pprint import pprint


class DataStatus:
    SUCCEEDED = 1
    ERROR = 2


class Direction(Enum):
    """
    can also use the oneliner format:
    class DirectionOneLiner(Enum):
        NORTH = 1; EAST = 2; SOUTH = 3; WEST = 4
    """
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

    def angle(self):
        right_angle = 90.0
        return right_angle * (self.value - 1)

    @ staticmethod
    def angle_interval(direction0, direction1):
        return abs(direction0.angle() - direction1.angle())


class DirectionRandomValue(Enum):
    """ The value can be random int values """
    NORTH = 111
    EAST = 222
    SOUTH = 333
    WEST = 444


class DirectionString(Enum):
    """ Or string """
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'


def use_regular_class_structure():
    """ Using regular class to store the data attributes without enum structure

        the implementation of enumeration with a regular class doesn’t have all
        the features that you may think of with enumerations in other programming
        languages. One such problem is shown below. In essence, such an implementation
        is “hacking” by utilizing the attributes of a Python class. Thus, if you
        check the type, you’ll find that it doesn’t behave ideally. In this case,
        the type is to be int, which reveals the type of the attribute. In other
        words, they’re not treated as members of a certain group. Instead, they’re
        simply separate attributes of the class, hence the instance type checking
        will be 'False'.
    """
    print()
    print(' Use Regular Class Structure '.center(50, '='))
    # Use the members
    print(f'{DataStatus.SUCCEEDED = }')
    print(f'Check Data type = {type(DataStatus.SUCCEEDED)}')
    print(f'Check Instance Type = {isinstance(DataStatus.SUCCEEDED, DataStatus)}')
    print(f'{DataStatus.ERROR = }')
    print(f'Check Data type = {type(DataStatus.ERROR)}')
    print(f'Check Instance Type = {isinstance(DataStatus.ERROR, DataStatus)}')


def use_enum_direction():
    print()
    print(' Use Enum Direction Class Structure '.center(50, '='))
    print(f'{Direction.NORTH = }')
    print(f'Check Data type = {type(Direction.NORTH)}')
    print(f'Check Instance Type = {isinstance(Direction.NORTH, Direction)}')

    print(f'{DirectionRandomValue.SOUTH = }')
    print(f'Check Data type = {type(DirectionRandomValue.SOUTH)}')
    print(f'Check Instance Type = {isinstance(DirectionRandomValue.SOUTH, DirectionRandomValue)}')

    print(f'{DirectionString.EAST = }')
    print(f'Check Data type = {type(DirectionString.EAST)}')
    print(f'Check Instance Type = {isinstance(DirectionString.EAST, DirectionString)}')


def access_enum_members():
    """
    For each member, it has additional attributes. The useful ones include name and value,
    which represent the enumerated member’s name and its associated value, integer, or
    string if you define it as such.
    """
    print()
    print(' Access Enum Direction Class Structure '.center(50, '='))
    # Create a member
    north = Direction.NORTH
    print(f'{north = }')

    # Check the name and the value
    print(f'{north.name = }')
    print(f'{north.value = }')

    # Direct access
    print(f'{DirectionRandomValue.WEST.name = }')
    print(f'{DirectionRandomValue.WEST.value = }')


def fetch_enum_member_values():
    """
    Notably, we use the identity comparison here by using the is keyword because
    you can think of members as singleton instance objects of the enumeration class.
    However, you’ll still get valid comparison results if you use equality comparisons
    using ==, which compares the values.
    """
    print()
    print(' Fetch Enum Direction Class Member Value '.center(50, '='))
    # Create a member from an integer value
    fetched_direction_value = 2
    fetched_direction = Direction(fetched_direction_value)
    print("Fetched Direction:", fetched_direction)
    # Condition evaluations
    print("Is the fetched direction north?", fetched_direction is Direction.NORTH)
    print("Is the fetched direction east?", fetched_direction is Direction.EAST)

    # Direct accessing the name and value of the enum members
    print(f'{DirectionRandomValue["EAST"] = }')
    print(f'{DirectionRandomValue(444) = }')


def enum_iteration_and_list():
    """ Enum iteration and list characteristics """
    print()
    print(' Iteration and List '.center(50, '='))

    print('Example 1: For Loop')
    for direction in Direction:
        print(direction)

    print('\nExample 2: List Function')
    pprint(f'List of Direction: {list(DirectionRandomValue)}')

    print('\nExample 3: List Comprehension')
    pprint([dir.name for dir in DirectionRandomValue])

    print('\nExample 4: For Loop with Dict Items')
    for name, direction in DirectionString.__members__.items():
        print(f"* Name: {name:<5}; * Direction: {direction}")


def expand_enum_class_with_methods():
    """ Embed methods in the enum class """
    print()
    print(' Embed methods in the enum class '.center(50, '='))

    east = Direction.EAST
    print("South Angle:", east.angle())
    west = Direction.WEST
    print("Angle Interval:", Direction.angle_interval(east, west))


def enum_functional_api():
    """
    Python provides functional APIs for the purpose of creating enumeration.
    If you don’t know what a functional API is, here’s an intuitive explanation.
    In our previous sections, we created enumeration members through a definition
    of a subclass of the Enum class. As you may know, it’s mostly an object-oriented
    programming (OOP) style. Basically, we use classes and objects to handle
    members. By contrast, the functional APIs take a functional approach. We
    create enumerations simply by calling a function.
    """
    print()
    print(' Enum Functional API '.center(50, '='))

    # Create an Enum class using the functional API
    DirectionFunctional = Enum("DirectionFunctional", "NORTH EAST SOUTH WEST")

    # Check what the Enum class is
    pprint(DirectionFunctional)

    # Check the items
    pprint(f'{list(DirectionFunctional) = }')
    pprint(f'{DirectionFunctional.__members__.items() = }')

    # Create a function and patch it to the DirectionFunctional class
    def angle(DirectionFunctional):
        right_angle = 90.0
        return right_angle * (DirectionFunctional.value - 1)

    DirectionFunctional.angle = angle

    # Create a member and access its angle
    south = DirectionFunctional.SOUTH
    print("South Angle:", south.angle())
    """ As shown above, we first created a function and assigned the function 
    to the DirectionFunctional class’s angle attribute. Notably, this attribute 
    is considered an instance method because the angle function’s first argument 
    is the class name. It’s the same as the self argument in the function declared 
    in the class. """


def use_enum_items_as_dict_keys():
    """
    This will be extremely helpful because it can also prevent us from making typos
    for the dictionary keys! When we want to get the value from its key in a dictionary,
    we will also be using the enumeration member.
    """
    print()
    print(' Use Enum Items as Dict Keys '.center(50, '='))

    direction_dict = {}
    direction_dict.setdefault(Direction.NORTH, 'Black Tortoise; Winter')
    direction_dict.setdefault(Direction.EAST, 'Azure Dragon; Spring')
    direction_dict.setdefault(Direction.SOUTH, 'Vermilion Bird; Summer')
    direction_dict.setdefault(Direction.WEST, 'White Tiger; Autumn')
    pprint(f'{direction_dict = }')


if __name__ == '__main__':
    use_regular_class_structure()
    use_enum_direction()
    access_enum_members()
    fetch_enum_member_values()
    enum_iteration_and_list()
    expand_enum_class_with_methods()
    enum_functional_api()
    use_enum_items_as_dict_keys()
