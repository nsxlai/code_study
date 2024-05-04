import pytest
from PYTEST.freeCodeCamp.source.my_functions import add, divide


def test_add():
    result = add(num1=1, num2=4)
    assert result == 5


def test_divide():
    result = divide(num1=10, num2=5)
    assert result == 2

