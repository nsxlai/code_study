"""
source: https://towardsdatascience.com/solid-coding-in-python-1281392a6a94
"""
import numpy as np
from abc import ABC, abstractmethod


class Operations(ABC):
    """Operations"""
    @abstractmethod
    def operation(list_: list) -> None:
        pass


class Mean(Operations):
    """Compute Max"""
    @staticmethod
    def operation(list_: list) -> None:
        print(f"The mean is {np.mean(list_)}")


class Max(Operations):
    """Compute Max"""
    @staticmethod
    def operation(list_: list) -> None:
        print(f"The max is {np.max(list_)}")


class Main:
    """Main"""
    @staticmethod
    def get_operations(list_: list) -> None:
        # __subclasses__ will found all classes inheriting from Operations
        print(f'{Operations.__subclasses__() = }')
        for operation in Operations.__subclasses__():
            operation.operation(list_)


if __name__ == "__main__":
    Main.get_operations([1, 2, 3, 4, 5])
