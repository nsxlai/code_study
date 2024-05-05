"""
code is sourced from PYTHON_STRUCTUR_STUDY/example_03_float_num_check/float_num_FSM.py
"""
import inspect
from collections import namedtuple


tok_next_t = namedtuple('tok_next_t', ['tokens', 'next_state'])


class myFSM:
    def __init__(self):
        self.tok_next = {}

    def add_state(self, name, tokens, next_state):
        # tok_next is a list of tok_next_t namedtuples
        # i.e. a list of the valid tokens and transition states

        if name not in self.tok_next:
            # It is possible there are several possible next states. Use the list to contain the next state
            self.tok_next[name] = []
        self.tok_next[name].append(tok_next_t(tokens, next_state))

    def run(self, cargo):
        orig_num = cargo
        state = "START"
        err = ""
        while True:
            if len(cargo) > 0:
                # Get next token (i.e. character) and remove it from the string
                token = cargo[0]
                cargo = cargo[1:]
                found = False
                for tn in self.tok_next[state]:
                    if token in tn.tokens:
                        # Token is valid, jump to next state
                        state = tn.next_state
                        found = True
                        break

                if not found:
                    # Token not found, switch to ERROR state
                    err = "Got " + token + " in state " + state
                    state = "ERROR"
            else:
                # No more characters left
                # * in the state name means it is a valid place to end
                if '*' in state:
                    state = "GOOD"
                else:
                    err = "More needed."
                    state = "ERROR"

            if state == "GOOD":
                print(orig_num + " is good.")
                break
            if state == "ERROR":
                print(orig_num + " is bad: " + err)
                break


if __name__ == '__main__':
    print(inspect.getsource(myFSM))
