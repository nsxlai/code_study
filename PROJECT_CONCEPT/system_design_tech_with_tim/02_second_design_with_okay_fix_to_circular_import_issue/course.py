"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial

Adding typing to each of the variable input
"""
from professor import Professor
from enroll import Enroll
from custom_exception import ProfessorError, EnrollmentError
from typing import Union, List


class Course:
	def __init__(self, name: str, code: str, max_: int, min_: int, professor: Union[Professor, List]):
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

	def add_professor(self, professor: Professor):
		if not isinstance(professor, Professor):
			raise ProfessorError("Invalid professor...")
		self.professors.append(professor)

	def add_enrollment(self, enroll: Enroll):
		if not isinstance(enroll, Enroll):
			raise EnrollmentError("Invalid enrollment...")

		if len(enroll) == self.max:
			raise EnrollmentError("Cannot enroll, course is full...")

		self.enrollments.append(enroll)

	def is_cancelled(self) -> bool:
		return len(self.enrollments) < self.min
