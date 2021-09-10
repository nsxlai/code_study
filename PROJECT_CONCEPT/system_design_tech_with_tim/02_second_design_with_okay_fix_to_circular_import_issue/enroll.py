"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial

Move 'from course import Course' to line 15
Move 'from student import Student' to line 16
To avoid circular import issue
"""
# from course import Course
# from student import Student
from datetime import datetime
from custom_exception import CourseError, StudentError


class Enroll:
	def __init__(self, student, course):
		from course import Course
		from student import Student
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
