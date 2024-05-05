"""
source: https://www.youtube.com/watch?v=6thjSbJcoUc
Tech with Tim: Software Design Tutorial

Add typing to the code
"""
from address import Address
from custom_exception import AddressError


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

	def add_address(self, address):
		if not isinstance(address, Address):
			raise AddressError("Invalid Address...")

		self.addresses.append(address)
