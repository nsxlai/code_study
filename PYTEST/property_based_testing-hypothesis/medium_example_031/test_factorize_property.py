# source: https://levelup.gitconnected.com/unit-testing-in-python-property-based-testing-892a741fc119
# Third party
import hypothesis.strategies as s
from hypothesis import given, settings, Verbosity

# First party
from factorize import factorize, factorize_rf


@given(s.integers(min_value=-(10 ** 6), max_value=10 ** 6))
def test_factorize_multiplication_property(n):
    """The product of the integers returned by factorize(n) needs to be n."""
    factors = factorize(n)
    product = 1
    for factor in factors:
        product *= factor
    assert product == n, f"factorize({n}) returned {factors}"


@settings(verbosity=Verbosity.verbose)
@given(s.integers(min_value=-(10 ** 6), max_value=10 ** 6))
def test_factorize_rf_multiplication_property(n):
    """The product of the integers returned by factorize(n) needs to be n.
       For verbose output, use the following command (with verbosity)
       pytest -s -v test_factorize_property.py::test_factorize_rf_multiplication_property
    """
    factors = factorize_rf(n)
    product = 1
    for factor in factors:
        product *= factor
    assert product == n, f"factorize({n}) returned {factors}"
