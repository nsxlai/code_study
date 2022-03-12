"""
source: https://levelup.gitconnected.com/10-interesting-python-programs-with-code-b676181a2d1a
"""
from faker import Faker


if __name__ == '__main__':
    fake_person = Faker()
    print(f'{fake_person.name() = }')
    print(f'{fake_person.email() = }')
    print(f'{fake_person.country() = }')
    print(f'{fake_person.profile() = }')
    print(f'{dir(fake_person) = }')
