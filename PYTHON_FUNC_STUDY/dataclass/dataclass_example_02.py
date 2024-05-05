# source: https://medium.com/better-programming/exploring-data-classes-in-python-66b696506e55
from dataclasses import dataclass


@dataclass
class Employee:
    name: str
    id: int
    salary: int
    designation: str

    def claculateSalaryPerAnum(self):
        return 12 * self.salary


@dataclass
class EmployeeWithBenefits(Employee):
    # If any of the Employee attributes have default value, the inheritance_with_test will have TypeError
    # TypeError: non-default argument 'healthBenefit' follows default argument
    healthBenefit: bool
    stocksBenefit: bool


if __name__ == '__main__':
    employee = Employee(name="Sam", id=1, salary=15000, designation="Developer")
    print("annual salary = ", employee.claculateSalaryPerAnum())
    # OutPut annual
    salary = 180000

    # Inheritance
    e = EmployeeWithBenefits(healthBenefit=True, stocksBenefit=False,
                             name="Sam", id=1, salary=15000, designation="Developer")
    print(e)

    # OutPut
    EmployeeWithBenefits(name='Sam', id=1, salary=15000, designation='Developer', healthBenefit=True, stocksBenefit=False)
    print(f'{e.name = }')
    print(f'{e.id = }')
    print(f'{e.salary = }')
    print(f'{e.designation = }')
    print(f'{e.healthBenefit = }')
    print(f'{e.stocksBenefit = }')
