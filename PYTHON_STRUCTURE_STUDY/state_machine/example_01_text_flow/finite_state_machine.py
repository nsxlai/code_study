# source: https://www.python-course.eu/finite_state_machine.php
from typing import Tuple, Any, Callable, Optional


class InitializationError(Exception):
    pass


class StateMachine:
    def __init__(self):
        self.handlers = {}  # handlers is the dictionary that maps STATE with TransitionFunction
        self.startState = None
        self.endStates = []

    def add_state(self, name: str, handler: Optional[Callable[[str], Tuple[str, str]]], end_state: bool = False):
        name = name.upper()
        self.handlers[name] = handler
        print(f'{self.handlers = }')
        if end_state:
            self.endStates.append(name)

    def set_start(self, name: str):
        self.startState = name.upper()

    def run(self, cargo: str):
        if self.startState is None:
            raise InitializationError("must call .set_start() before .run()")

        if not self.endStates:
            raise InitializationError("at least one state must be an end_state")

        while True:
            (newState, cargo) = handler(cargo)
            if newState.upper() in self.endStates:
                print("reached ", newState)
                break
            else:
                handler = self.handlers[newState.upper()]
                print(f'{handler = }')


def start_transitions(txt: str) -> Tuple[str, str]:
    splitted_txt = txt.split(' ', 1)
    print(f'{txt = }; {splitted_txt = }')
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt, '')
    if word == "Python":
        newState = "Python_state"
    else:
        newState = "error_state"
    return newState, txt


def python_state_transitions(txt):
    splitted_txt = txt.split(' ', 1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt, '')
    if word == "is":
        newState = "is_state"
    else:
        newState = "error_state"
    return newState, txt


def is_state_transitions(txt):
    splitted_txt = txt.split(' ', 1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt, '')
    if word == "not":
        newState = "not_state"
    elif word in positive_adjectives:
        newState = "pos_state"
    elif word in negative_adjectives:
        newState = "neg_state"
    else:
        newState = "error_state"
    return newState, txt


def not_state_transitions(txt: str) -> Tuple[str, str]:
    splitted_txt = txt.split(' ', 1)
    word, txt = splitted_txt if len(splitted_txt) > 1 else (txt, '')
    if word in positive_adjectives:
        newState = "neg_state"
    elif word in negative_adjectives:
        newState = "pos_state"
    else:
        newState = "error_state"
    return newState, txt


# def neg_state(txt: str) -> Tuple[str, str]:
#     print("Hallo")
#     return "neg_state", ""


if __name__ == "__main__":
    positive_adjectives = ["great", "super", "fun", "entertaining", "easy"]
    negative_adjectives = ["boring", "difficult", "ugly", "bad"]

    m = StateMachine()
    m.add_state("Start", start_transitions)
    print(f'{m.handlers = }')
    m.add_state("Python_state", python_state_transitions)
    m.add_state("is_state", is_state_transitions)
    m.add_state("not_state", not_state_transitions)
    m.add_state("neg_state", None, end_state=True)
    m.add_state("pos_state", None, end_state=True)
    m.add_state("error_state", None, end_state=True)
    m.set_start("Start")
    m.run("Python is great")
    m.run("Python is difficult")
    m.run("Perl is ugly")
