"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial
"""
from person import Person
from enroll import Enroll
from address import Address
from custom_exception import EnrollmentError


class Student(Person):
	PART_TIME_LIMIT = 3

	def __init__(self, first: str, last: str, dob: str, phone: str, address: Address, international=False):
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
