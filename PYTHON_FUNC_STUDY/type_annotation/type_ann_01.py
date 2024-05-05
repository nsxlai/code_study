# source: https://docs.python.org/3/library/typing.html
from typing import Any, Dict, Optional, Any, ClassVar, Type


class typeStrange:
    def __init__(self):
        self.internalDict: ClassVar[Dict[str, Type[typeStrange]]] = {}

    def dict_element(self):
        return self.internalDict.items()


def printDict(input_dict: Dict[str, int]) -> int:
    for key, value in input_dict.items():
        print(f'{key = }, {value = }')
    return len(input_dict)


def diff_out(in_str: str) -> Optional[str]:
    ''' Optional out mean the return can be specified type or None'''
    if in_str.isnumeric():
        return 'String is numeric'
    else:
        return None


def proc_dict(in_dict: Dict[str, int]) -> Any:
    temp = 0
    for key, value in in_dict.items():
        temp += value
    return temp


Vector = list[float]


def scale(scalar: float, vector: Vector) -> Vector:
    return [scalar * num for num in vector]


if __name__ == '__main__':
    test_dict = {'test001': 112, 'test002': 202, 'test003': 57, 'test004': 76, 'test005': 189}
    printDict(test_dict)

    null_dict = {}
    print(printDict(null_dict))

    print(f'{diff_out("10") = }')
    print(f'{diff_out("test_phrase") = }')

    print(f'{proc_dict(test_dict) = }')

    # typechecks; a list of floats qualifies as a Vector.
    new_vector = scale(2.0, [1.0, -4.2, 5.4])