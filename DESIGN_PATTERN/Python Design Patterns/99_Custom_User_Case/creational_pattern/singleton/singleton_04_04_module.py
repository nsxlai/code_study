"""
source: https://medium.com/@aditi-mishra/singleton-pattern-in-python-libraries-8509903fb474

4. Using module to implement the singleton pattern
=> This is the most frequent one that is used by python developers.
   There have been debates around which one of these is the best singleton implementation.
"""


class Singleton():
    def __init__(self) -> None:
        self.dummy = "dummy"


s1 = Singleton()
