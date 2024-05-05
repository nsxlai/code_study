from dataclasses import dataclass
from typing import Any, Dict, Callable
import hypothesis.strategies as st


@dataclass
class GeneratedData:
    array_length: st.SearchStrategy[int]
    dist: st.SearchStrategy[Callable]
    perc: st.SearchStrategy[float]


@st.composite
def generate_scenario(draw, settings: Any) -> Dict[str, Any]:
    """
    Generate a testing scenario for the percentile function.
    :param draw: Hypothesis object used to draw examples.
    :param settings: Setting for the generation of test data.
    :return: A tuple of two generated texts.
    """
    dist = draw(settings.dist)
    n = draw(settings.array_length)
    arr = dist(size=n)

    perc = draw(settings.perc)

    return {"values": arr, "perc": perc}
