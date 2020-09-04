import hypothesis.strategies as st
from hypothesis import given, settings, assume

from binary_serach_01 import index_equals_value_search


@given(st.lists(st.integers(), min_size=1, max_size=10).map(sorted))
def test_binary_search(integer_list) -> None:
    """
    Test the percentile function.
    :param data: Hypothesis DataObject that is used to draw from our strategies.
    """

    # test_data = data.draw(generate_scenario(settings=SETTINGS))
    # print(f'{test_data = }')
    # Property 1: Order should not matter
    val = index_equals_value_search(integer_list)
    # print(f'{val = }')
    assert interger_list[val] == val
