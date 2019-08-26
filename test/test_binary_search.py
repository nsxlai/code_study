from ..binary_search.binary_search_02 import find_ceiling
from ..binary_search.binary_search_01 import index_equals_value_search
from ..binary_search.binary_search_03 import find_mind_diff
from pytest import mark


@mark.bst1
def test_binary_search_01():
    arr = [-5, -2, 0, 1, 4, 7, 9, 12, 15, 20]
    result = index_equals_value_search(arr)
    assert result == 4


@mark.bst2
def test_binary_search_02_case_01():
    arr = [-5, -2, 0, 1, 4, 7, 9, 12, 15, 20]
    key = 13
    result = find_ceiling(arr, key)
    assert result == 15


@mark.bst2
def test_binary_search_02_case_02():
    arr = [-10, -18, -15, -10, -5, -2, 3, 6, 7, 10, 14, 17, 20]
    key = -3
    result = find_ceiling(arr, key)
    assert result == -2


@mark.bst2
def test_binary_search_02_case_03():
    arr = [3, 5, 10, 17]
    key = -3
    result = find_ceiling(arr, key)
    assert result == 3


@mark.bst3
def test_binary_search_03_case_01():
    arr = [-10, -8, -3, 0, 4, 8, 14, 20]
    key = 10
    result = find_mind_diff(arr, key)
    assert result == 8