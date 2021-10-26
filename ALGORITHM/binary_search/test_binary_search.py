from .binary_search_02 import find_ceiling
from .binary_search_01 import index_equals_value_search
from .binary_search_03 import find_min_diff
from pytest import mark, fixture
from unittest.mock import Mock, patch


@mark.parametrize('arr, arr_result',
                  [([-5, -2, 0, 1, 4, 7, 9, 12, 15, 20], 4),
                  ([0, 3, 6], 0),
                  ([-10, -5, 0, 1, 3, 5, 6, 8, 10], 5)])
def test_binary_search_01(arr, arr_result):
    result = index_equals_value_search(arr)
    print(f' Funtion output is {result}')
    assert result == arr_result


test_params_bst2 = [([-5, -2, 0, 1, 4, 7, 9, 12, 15, 20], 13, 15),
                    ([-10, -18, -15, -10, -5, -2, 3, 6, 7, 10, 14, 17, 20], -3, -2),
                    ([3, 5, 10, 17], -3, 3),
                   ]


# @mark.bst2
@mark.parametrize('arr, key, arr_result', test_params_bst2)
def test_binary_search_02(arr, key, arr_result):
    result = find_ceiling(arr, key)
    assert result == arr_result


test_params_bst3 = [
    ([-10, -8, -3, 0, 4, 8, 14, 20], 10),
    ([-10, -8, -3, 0, 1, 3, 4, 8, 14, 20], 8),
    ([0, 2, 4, 6, 8, 10, 14, 20, 22, 30], 0),
    ([1, 2, 3, 4, 5, 6], 1)
]


# @mark.bst3
@mark.parametrize('arr, key', test_params_bst3)
def test_binary_search_03(arr, key):
    result = find_min_diff(arr, key)
    print(result)
    # assert result == arr_result
