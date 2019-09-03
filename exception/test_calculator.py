from unittest import TestCase
from .hackerrank_exception import Calculator
from pytest import mark
from pytest import fixture


# Unittest way of testing the method
class TestCalculator(TestCase):
    def test_power(self):
        self.calculator = Calculator()
        self.assertEqual(self.calculator.power(2, 3), 8)
        self.assertEqual(self.calculator.power(0, 3), 0)
        self.assertEqual(self.calculator.power(0, 1), 1)
        self.assertEqual(self.calculator.power(10, 3), 1000)
        self.assertEqual(self.calculator.power(5, 3), 125)

# Below is the pytest way using mark.parametrize
test_power_params = [
    (2, 3, 8),
    (0, 3, 0),
    (0, 1, 0),
    (10, 3, 1000),
    (5, 3, 125),
    (-1, 5, 'n and p should be non-negative'),
    (4, -3, 'n and p should be non-negative'),
    (-3, -2, 'n and p should be non-negative'),
]


@mark.parametrize('n, p, expected_result', test_power_params)
def test_power_with_mark_parametrize(n, p, expected_result):
    calculator = Calculator()
    result = calculator.power(n, p)
    if type(result) != int:
        # Special case if result is ValueError
        result = 'n and p should be non-negative'
    assert result == expected_result


@mark.skip
@fixture(params=['test01', 'test02'])
def test_power_with_fixture(request):
    if request.params == 'test01':
        print(request.params)
    elif request.params == 'test02':
        print(request.params)
    assert True