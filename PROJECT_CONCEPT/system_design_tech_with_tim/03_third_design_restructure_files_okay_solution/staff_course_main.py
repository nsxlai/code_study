"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial
"""
from address import Address
# from enroll import Enroll
from typing import List, Union
from custom_exception import EnrollmentError, AddressError, ProfessorError, CourseError, StudentError
from datetime import datetime


class Person:
    def __init__(self, first: str, last: str, dob: str, phone: str, address: Address):
        self.first_name = first
        self.last_name = last
        self.date_of_birth = dob
        self.phone = phone
        self.addresses = []

        if isinstance(address, Address):
            self.addresses.append(address)
        elif isinstance(address, list):
            for entry in address:
                if not isinstance(entry, Address):
                    raise AddressError("Invalid Address...")

            self.addresses = address
        else:
            raise AddressError("Invalid Address...")

    def add_address(self, address: Address):
        if not isinstance(address, Address):
            raise AddressError("Invalid Address...")

        self.addresses.append(address)


class Course:
    def __init__(self, name: str, code: str, max_: int, min_: int, professor: Union[Person, List]):
        self.name = name
        self.code = code
        self.max = max_
        self.min = min_
        self.professors = []
        self.enrollments = []

        if isinstance(professor, Professor):
            self.professors.append(professor)
        elif isinstance(professor, list):
            for entry in professor:
                if not isinstance(entry, Professor):
                    raise ProfessorError("Invalid professor...")
            self.professors = professor
        else:
            raise ProfessorError("Invalid professor...")

    def add_professor(self, professor: Person):
        if not isinstance(professor, Professor):
            raise ProfessorError("Invalid professor...")
        self.professors.append(professor)

    # Cannot have add_enrollment in this class. This will create circular function reference. Will add this function
    # outside of the class
    # def add_enrollment(self, enroll: Enroll):
    #     if not isinstance(enroll, Enroll):
    #         raise EnrollmentError("Invalid enrollment...")
    #
    #     if len(enroll) == self.max:
    #         raise EnrollmentError("Cannot enroll, course is full...")
    #
    #     self.enrollments.append(enroll)

    def is_cancelled(self) -> bool:
        return len(self.enrollments) < self.min


class Professor(Person):
    BONUS_AMOUNT = 20_000

    def __init__(self, first: str, last: str, dob: str, phone: str, address: Address, salary: float):
        super().__init__(first, last, dob, phone, address)
        self.salary = salary
        self.courses = []
        self.got_raise = False

    def check_for_raise(self):
        if len(self.courses) >= 4 and not self.got_raise:
            self.salary += self.BONUS_AMOUNT
            self.got_raise = True

    def add_course(self, course: Course):
        if not isinstance(course, Course):
            raise CourseError("Invalid Course...")
        self.courses.append(course)


class Enroll:
    def __init__(self, student: Person, course: Course):
        if not isinstance(student, Student):
            raise StudentError("Invalid student...")

        if not isinstance(course, Course):
            raise CourseError("Invalid course...")

        self.student = student
        self.course = course
        self.grade = None
        self.date = datetime.now()
        self.grade = 0

    def set_grade(self, grade: int):
        self.grade = grade


class Student(Person):
    PART_TIME_LIMIT = 3

    def __init__(self, first: str, last: str, dob: str, phone: str, address: Address, international = False):
        super().__init__(first, last, dob, phone, address)
        self.international = international
        self.enrolled = []

    def add_enrollment(self, enroll: Enroll):
        if not isinstance(enroll, Enroll):
            raise EnrollmentError("Invalid Enroll...")

        self.enrolled.append(enroll)

    def is_on_probation(self):
        return False

    def is_part_time(self):
        return len(self.enrolled) <= self.PART_TIME_LIMIT


class StudentEnrollment:
    def __init__(self, student: Student):
        self.student = student
        self.enrollments = []

    def add_enrollment(self, enroll: Enroll):
        if not isinstance(enroll, Enroll):
            raise EnrollmentError("Invalid enrollment...")

        # if len(enroll) >= max_enroll_count:
        #     raise EnrollmentError("Cannot enroll, course is full...")

        return self.enrollments.append(enroll)


if __name__ == '__main__':
    student_sample = {
        1: {'first': 'John', 'last': 'Smith', 'dob': '01/01/1990', 'phone': '123456789',
            'address': Address(country='USA', state='CA', city='San Francisco', street='123 Maple Street',
                               postal_code='94678')
            },
        2: {'first': 'Summer', 'last': 'Tan', 'dob': '07/01/1995', 'phone': '987654321',
            'address': Address(country='USA', state='CA', city='San Diego', street='456 Bee Street',
                               postal_code='93838')
            },
    }

    professor_sample = {
        1: {'first': 'Akiko', 'last': 'Imari', 'dob': '01/01/1985', 'phone': '3333333333',
            'address': Address(country='USA', state='CA', city='San Jose', street='889 High Street',
                               postal_code='95145'),
            'salary': 100_000.00
            },
        2: {'first': 'Christina', 'last': 'Mori', 'dob': '01/01/1987', 'phone': '5555555555',
            'address': Address(country='USA', state='CA', city='Santa Cruz', street='512 Beach Street',
                               postal_code='98345'),
            'salary': 120_000.00
            },
    }

    s1 = Student(**student_sample.get(1))
    s2 = Student(**student_sample.get(2))
    p1 = Professor(**professor_sample.get(1))
    p2 = Professor(**professor_sample.get(2))

    math1 = Course(name='Math1', code='MA001', max_=50, min_=10, professor=p1)
    math2 = Course(name='Math2', code='MA002', max_=50, min_=10, professor=p1)
    chem1 = Course(name='Chem1', code='CH001', max_=30, min_=5, professor=p2)

    en_s1_c1 = Enroll(student=s1, course=math1)
    en_s1_c2 = Enroll(student=s1, course=chem1)

    en_s2_c1 = Enroll(student=s2, course=math2)
    en_s2_c2 = Enroll(student=s2, course=chem1)

    s1_en = StudentEnrollment(s1)
    s1_en.add_enrollment(en_s1_c1)
    s1_en.add_enrollment(en_s1_c2)

    s2_en = StudentEnrollment(s2)
    s2_en.add_enrollment(en_s2_c1)
    s2_en.add_enrollment(en_s2_c2)

    print(f'{s1_en = }')
    print(f'{s2_en = }')
