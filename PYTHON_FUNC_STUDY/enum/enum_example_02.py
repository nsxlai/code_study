# example from GAME/tic_tac_toe/logic/models.py
from __future__ import annotations  # Enable lazy evaluation of typing; use this to avoid potential circular reference

import enum


class Mark(enum.StrEnum):
    CROSS = 'X'
    NAUGHT = 'O'

    @property
    # def other(self) -> "Mark":  # Quote around Mark for not fully defined return type (will be determined at runtime)
    def other(self) -> Mark:  # with lazy evaluation enabled from the __future__ module, we can remove the double quote
        return Mark.CROSS if self is Mark.NAUGHT else Mark.NAUGHT


if __name__ == '__main__':

    print(f'{Mark.CROSS = }')
    print(f'{Mark.NAUGHT = }')
    print(f'{Mark["CROSS"] = }')
    print(f'{Mark["NAUGHT"] = }')
    print(f'{Mark("X") = }')
    print(f'{Mark("O") = }')
    print(f'{Mark("X").other = }')
    print(f'{Mark("O").other = }')
    print(f'{Mark("X").name = }')
    print(f'{Mark("X").value = }')
    print(f'{Mark("X") == "X" = }')
    print(f'{Mark("X") == "O" = }')
    print(f'{isinstance(Mark.CROSS, str) = }')
    print(f'{Mark.CROSS.lower() = }')

    for mark in Mark:
        print(f'{mark = }')

