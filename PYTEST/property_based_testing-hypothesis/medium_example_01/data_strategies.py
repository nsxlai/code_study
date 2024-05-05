from dataclasses import dataclass
import hypothesis.strategies as st


@dataclass
class GeneratedData:
    float_value: st.SearchStrategy[float]


generated_data = GeneratedData(float_value=st.floats(min_value=0.0, max_value=10.0))
