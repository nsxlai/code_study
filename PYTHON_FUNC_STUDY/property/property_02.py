from typing import List, Tuple

class Employee:
    def __init__(self, pid: int, first: str, last: str, salary: int):
        self.pid = pid
        self.first = first
        self.last = last
        self.salary = salary
        self.email_id = ''

    @property
    def email(self):
        self.email_id = f'{self.first}.{self.last}@email.com'
        # print(f'Email ID = {self.email_id}')
        return self.email_id

    @email.setter
    def email(self, email_id):
        self.email_id = email_id

    @property
    def fullname(self):
        return f'{self.first} {self.last}'

    def __repr__(self):
        return f"Employee('{self.first}, {self.last}, {self.salary}')"


if __name__ == '__main__':
    e = Employee(1, 'John', 'Smith', 90000)
    print(e)
    print(f'{e.email = }')  # 'email' is not treated as a method but rather a class attribute property
    print(f'{e.fullname = }')  # that's why no need for e.email() but e.email instead
