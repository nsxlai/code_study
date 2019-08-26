import unittest
from . import student_grade

"""
Sample Input

Heraldo Memelli 8135627
2
100 80
------------------------
Aakansha Doshi 7825621
4
31 32 34 35
"""


class student_grade_Tests(unittest.TestCase):
    def setup(self):
        self.s = student_grade.Student(firstName, lastName, idNum, scores)
        self.s.printPerson()