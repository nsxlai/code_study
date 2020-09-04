from typing import List, Union
import numpy as np


def calc_percentile(arr: List[Union[float, int]], perc: float) -> float:
    """
    Calculate the percentile value of an array (using midpoint interpolation).
    :param arr: An array containing float or integer values.
    :param perc: The percentile value that we want to calculate.
    :return: The perc. value.
    """
    arr.sort()
    n = len(arr)
    position_floor = int(np.floor(perc * (n - 1)))
    position_ceil = int(np.ceil(perc * (n - 1)))

    return (arr[position_floor] + arr[position_ceil]) / 2
