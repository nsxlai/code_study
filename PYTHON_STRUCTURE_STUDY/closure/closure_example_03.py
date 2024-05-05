# source: https://towardsdatascience.com/dont-use-recursion-in-python-any-more-918aad95094c
from dataclasses import dataclass
from typing import Callable


students = {
    'Alice': 98,
    'Bob': 67,
    'Chris': 85,
    'David': 75,
    'Ella': 54,
    'Fiona': 35,
    'Grace': 69,
    'Mary': 91,
    'Lily': 82,
    'John': 73,
    'Mason': 30,
    'Eaton': 45,
    'Zack': 95,
}


def make_student_classifier(lower_bound, upper_bound):
    def classify_student(exam_dict):
        return {k: v for (k, v) in exam_dict.items() if lower_bound <= v < upper_bound}
    return classify_student


@dataclass
class grade:
    grade_A: Callable = make_student_classifier(90, 100)
    grade_B: Callable = make_student_classifier(80, 90)
    grade_C: Callable = make_student_classifier(70, 80)
    grade_D: Callable = make_student_classifier(60, 70)
    grade_F: Callable = make_student_classifier(0, 60)


if __name__ == '__main__':
    s_grade = grade()
    print(f'{s_grade.grade_A(students) = }')
    print(f'{s_grade.grade_B(students) = }')
    print(f'{s_grade.grade_C(students) = }')
    print(f'{s_grade.grade_D(students) = }')
    print(f'{s_grade.grade_F(students) = }')
