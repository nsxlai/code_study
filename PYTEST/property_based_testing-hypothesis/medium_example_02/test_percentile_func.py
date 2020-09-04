import hypothesis.strategies as st
from hypothesis import given, settings, assume
import numpy as np

from percentile import calc_percentile
from percentile_strategies import GeneratedData, generate_scenario


settings.register_profile(
    "my_profile",
    max_examples=10000,
    deadline=60 * 1000,  # Allow 1 min per example (deadline is specified in milliseconds,
)


SETTINGS = GeneratedData(
    array_length=st.integers(2, 50000),
    dist=st.sampled_from([np.random.uniform, np.random.normal]),
    perc=st.floats(0.0, 1.0),
)


@given(st.data())
@settings(settings.load_profile("my_profile"))
def test_calc_percentile(data: st.DataObject) -> None:
    """
    Test the percentile function.
    :param data: Hypothesis DataObject that is used to draw from our strategies.
    """

    test_data = data.draw(generate_scenario(settings=SETTINGS))
    # print(f'{test_data = }')
    # Property 1: Order should not matter
    my_perc_val = calc_percentile(arr=test_data["values"], perc=test_data["perc"])

    # Invert the order of values
    inv_my_perc_val = calc_percentile(arr=test_data["values"][::-1], perc=test_data["perc"])

    assert my_perc_val == inv_my_perc_val

    # Property 2: Value should be equivalent to existing implementation
    # Numpy implementation
    numpy_per_val = np.percentile(a=test_data["values"], q=test_data["perc"] * 100, interpolation="midpoint")

    # Validate that the values are equivalent
    assert my_perc_val == numpy_per_val
