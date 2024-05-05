# source: https://towardsdatascience.com/automating-unit-tests-in-python-with-hypothesis-d53affdc1eba
import hypothesis.strategies as st
from hypothesis import given, settings, HealthCheck
from my_functions import convert_to_integer
from data_strategies import generated_data


settings.register_profile(
    "my_profile",
    max_examples=200,
    deadline=60 * 1000,  # Allow 1 min per example (deadline is specified in milliseconds)
    suppress_health_check=(HealthCheck.too_slow, HealthCheck.data_too_large),
)


@given(st.data())
@settings(settings.load_profile("my_profile"))
def test_convert_to_integer(test_data: st.DataObject):
    my_float = test_data.draw(generated_data.float_value)
    print(f'{my_float = }')
    float_to_int = convert_to_integer(my_float)
    assert isinstance(float_to_int, int)
