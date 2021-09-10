from pytest import mark
from . import student_grade
from student_grade import Student


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


# @mark.student_test
def test_student1(self):
    s1 = Student('Heraldo', 'Memelli', '8135627', [100, 80])
    s1.printPerson()
    print("Grade:", s1.calculate())


# @mark.student_test
def test_student2(self):
    s2 = Student('Aakansha', 'Doshi', '7825621', [31, 32, 34, 35])
    s2.printPerson()
    print("Grade:", s2.calculate())


# @mark.student_test
def test_student3(self):
    s3 = Student('John', 'Smith', '8342756', [67, 75, 83, 73])
    s3.printPerson()
    print("Grade:", s3.calculate())
