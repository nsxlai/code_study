"""
source: https://realpython.com/inheritance-composition-python/?utm_source=notification_summary&utm_medium=email&utm_campaign=2024-01-16

Since you don’t have to derive from a specific class for your objects to be reusable by the program,
you may be asking why you should use inheritance instead of just implementing the desired interface.
The following rules may help you to make this decision:

1. Use inheritance to reuse an implementation:
    Your derived classes should leverage most of their base class implementation.
    They must also model an is a relationship. A Customer class might also have an .id and a .name,
    but a Customer is not an Employee, so in this case, you shouldn’t use inheritance.

2. Implement an interface to be reused:
    When you want your class to be reused by a specific part of your application,
    you implement the required interface in your class, but you don’t need to provide a base class,
    or inherit from another class.
"""

from inheritance_composition_lib import SalaryEmployee, HourlyEmployee, CommissionEmployee, PayrollSystem


if __name__ == '__main__':

    salary_employee = SalaryEmployee(1, "John Smith", 1500)
    hourly_employee = HourlyEmployee(2, "Jane Doe", 40, 15)
    commission_employee = CommissionEmployee(3, "Kevin Bacon", 1000, 250)

    payroll_system = PayrollSystem()
    payroll_system.calculate_payroll(
        [salary_employee, hourly_employee, commission_employee]
    )

    # MRO = method resolution order; it displays the inheritance order
    print(f'{CommissionEmployee.__mro__ = }')
