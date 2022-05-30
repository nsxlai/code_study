"""
source: https://betterprogramming.pub/too-many-if-elif-conditions-in-python-use-dictionaries-instead-5486299af27e
"""


def original_code():
    user_input = input("Pick a color: green, blue, red, pink\n")

    if user_input == "green":
        # Execute some code
        print(f"{user_input = }")
    elif user_input == "blue":
        # Execute some code
        print(f"{user_input = }")
    elif user_input == "red":
        # Execute some code
        print(f"{user_input = }")
    elif user_input == "pink":
        # Execute some code
        print(f"{user_input = }")
    else:
        print('Did not select within the given color choices')


def green_function(color):
    # Execute some code
    print(f"{color} 1")


def blue_function(color):
    # Execute some code
    print(f"{color} 1")


def red_function(color):
    # Execute some code
    print(f"{color} 1")


def pink_function(color):
    # Execute some code
    print(f"{color} 1")


if __name__ == '__main__':
    # First execute the original code
    original_code()

    # Then execute the new dictionary based code:
    colors_dict = {
        "green": green_function,
        "blue": blue_function,
        "red": red_function,
        "pink": pink_function,
    }

    user_input = input("Pick a color: green, blue, red, pink\n")
    error_func = lambda x: print(f'Does not have {x} func available')
    colors_dict.get(user_input, error_func)(user_input)
