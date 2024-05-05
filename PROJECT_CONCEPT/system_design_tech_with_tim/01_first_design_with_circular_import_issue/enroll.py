"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial
"""
from course import Course
from student import Student
from datetime import datetime
from custom_exception import CourseError, StudentError


class Enroll:
	def __init__(self, student, course):
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
