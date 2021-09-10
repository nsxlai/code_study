"""
Several circular import issue:
Case 1:
First import from course.py => from course import Course
Then from staff_course_main.py => from professor import Professor
But the staff_course_main.py reference course.py => from course import Course
ImportError: cannot import name 'Course' from partially initialized module 'course'
(most likely due to a circular import)

Case 2:
First import from staff_course_main.py => from professor import Professor
Then from staff_course_main.py: from course import Course
But the course.py reference staff_course_main.py => from professor import Professor
ImportError: cannot import name 'Professor' from partially initialized module 'professor'
(most likely due to a circular import)
Process finished with exit code 1
"""
from course import Course
from enroll import Enroll
from address import Address
from professor import Professor
from student import Student


if __name__ == '__main__':
    student_sample = {
        1: {'first': 'John', 'last': 'Smith', 'dob': '01/01/1990', 'phone': '123456789',
            'address': Address(country='USA', state='CA', city='San Francisco', street='123 Maple Street', postal_code='94678')
            },
        2: {'first': 'Summer', 'last': 'Tan', 'dob': '07/01/1995', 'phone': '987654321',
            'address': Address(country='USA', state='CA', city='San Diego', street='456 Bee Street', postal_code='93838')
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

    print(f'{en_s1_c1 = }')
    print(f'{en_s2_c1 = }')
