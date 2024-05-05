"""
Source: Youtube video "Gary Explains": Understanding Finite State Machines (or Finite-State Automation)
https://www.youtube.com/watch?v=2OiWs-h_M3A&t=252s
"""
from typing import Tuple


def state_start_handler(cargo: int) -> Tuple[str, int]:
    return 'RED', cargo


def state_red_handler(cargo: int) -> Tuple[str, int]:
    print('RED')
    return 'RED_AMBER', cargo


def state_red_amber_handler(cargo: int) -> Tuple[str, int]:
    print('RED & AMBER')
    return 'GREEN', cargo


def state_green_handler(cargo: int) -> Tuple[str, int]:
    print('GREEN')
    return 'AMBER', cargo


def state_amber_handler(cargo: int) -> Tuple[str, int]:
    print('AMBER')
    cargo -= 1
    if cargo > 0:
        return 'RED', cargo
    else:
        return 'END', cargo


class myFSM:
    def __init__(self):
        self.handlers = {}

    def add_state(self, name, handler):
        self.handlers[name] = handler

    def run(self, startingState, cargo):
        handler = self.handlers[startingState]
        while True:
            newState, cargo = handler(cargo)
            if newState == 'END':
                print('END reached!')
                break
            handler = self.handlers[newState]


if __name__ == '__main__':
    fsm = myFSM()
    fsm.add_state('START', state_start_handler)
    fsm.add_state('RED', state_red_handler)
    fsm.add_state('RED_AMBER', state_red_amber_handler)
    fsm.add_state('GREEN', state_green_handler)
    fsm.add_state('AMBER', state_amber_handler)

    print(' Run #1 '.center(30, '-'))
    fsm.run('START', 3)
    print(' Run #2 '.center(30, '-'))
    fsm.run('AMBER', 4)
