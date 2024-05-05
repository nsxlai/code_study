from abc import ABC, abstractmethod
from typing import Any, List


class fileTypeExec(ABC):
    """ Interface for the file type """
    def execute(self, input_filetype: Any) -> Any:
        pass


class stringType(fileTypeExec):
    def execute(self, val: str) -> str:
        print(f'{type(val) = }')
        return 'User input file type: ' + val


class intType(fileTypeExec):
    def execute(self, val: int) -> int:
        print(f'{type(val) = }')
        return val + 100


class floatType(fileTypeExec):
    def execute(self, val: float) -> int:
        print(f'{type(val) = }')
        return val // 1


class listNumType(fileTypeExec):
    def execute(self, val: List[int]) -> int:
        print(f'{type(val) = }')
        return sum(val)


class listStrType(fileTypeExec):
    def execute(self, val: List[str]) -> str:
        print(f'{type(val) = }')
        return ' '.join(val)


if __name__ == '__main__':
    print(f'{fileTypeExec.__subclasses__() = }')
