"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial
"""
from person import Person
from course import Course
from address import Address
from custom_exception import CourseError


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

	def add_course(self, course):
		if not isinstance(course, Course):
			raise CourseError("Invalid Course...")
		self.courses.append(course)
