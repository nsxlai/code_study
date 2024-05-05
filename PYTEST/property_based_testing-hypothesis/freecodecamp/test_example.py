# source: https://www.freecodecamp.org/news/intro-to-property-based-testing-in-python-6321e0c2f8b/
import pytest


def sum(num1, num2):
    """It returns sum of two numbers"""
    return num1 + num2


# make sure to start function name with test
def test_sum():
    assert sum(1, 2) == 3


@pytest.mark.parametrize('num1, num2, expected',
                         [(3, 5, 8),
                          (-2, -2, -4),
                          (-1, 5, 4),
                          (3, -5, -2),
                          (0, 5, 5)])
def test_sum1(num1, num2, expected):
    assert sum(num1, num2) == expected

"""
Issue 1: Test exhaustiveness depends on the person writing the test
They may choose to write 5 or 50 or 500 test cases but still remain unsure whether they have safely covered most, if not all, the edge cases.

This brings us to our second pain point:

Issue 2 — Non-robust tests due to unclear/ambiguous requirement understanding
When we were told to write our sum function, what specific details were conveyed?

Were we told:

what kind of input our function should expect?
how our function should behave in unexpected input scenarios?
what kind of output our function should return?
To be more precise, if you consider the sum function we have written above:

do we know if num1, num2 should be an int or float? Can they also be sent as type string or any other data type?
what is the minimum and maximum value of num1 and num2 that we should support?
how should the function behave if we get null inputs?
should the output returned by the sum function be int or float or string or any other data type?
in what scenarios should it display error messages?
"""


def sum_bad(num1, num2):
    """Buggy logic"""
    if num1 == 3 and num2 == 5:
        return 8
    elif num1 == -2 and num2  == -2 :
        return -4
    elif num1 == -1 and num2 == 5 :
        return 4
    elif num1 == 3 and num2 == -5:
        return -2
    elif num1 == 0 and num2 == 5:
        return 5


@pytest.mark.parametrize('num1, num2, expected',
                         [(3, 5, 8),
                          (-2, -2, -4),
                          (-1, 5, 4),
                          (3, -5, -2),
                          (0, 5, 5)])
def test_sum2(num1, num2, expected):
    assert sum_bad(num1, num2) == expected


# Property based testing
from hypothesis import given, settings, Verbosity, example
import hypothesis.strategies as st


@settings(verbosity=Verbosity.verbose)
@given(st.integers(), st.integers())
def test_sum3(num1, num2):
    """ The verbosity will pipe the verbose output in pytest. Use the following command:
        pytest test_example.py::test_sum3 -v -s
    """
    assert sum(num1, num2) == num1 + num2


# To manually inject test cases from user, use @example
@settings(verbosity=Verbosity.verbose)
@given(st.integers(), st.integers())
@example(1, 2)
def test_sum4(num1, num2):
    assert sum(num1, num2) == num1 + num2


@settings(verbosity=Verbosity.verbose)
@given(st.integers(), st.integers())
def test_sum5(num1, num2):
    assert sum(num1, num2) == num1 + num2

    # Test Identity property
    assert sum(num1, 0) == num1

    # Test Commutative property
    assert sum(num1, num2) == sum(num2, num1)
