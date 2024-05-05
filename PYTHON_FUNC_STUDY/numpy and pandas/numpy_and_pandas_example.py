import numpy as np
import pandas as pd
from math import sqrt


def header(text: str):
    print('\n' + text.center(50, '='))


def np_concat():
    header('NP Concatenate (np.c_)')
    point = np.array([[5, 3], [3, -4], [-2, -4], [-3, 5]])
    print(f'point = \n{point}\n')

    dist = [sqrt(point[i, 0] ** 2 + point[i, 1] ** 2) for i in range(4)]
    print(f'dist = \n{dist}\n')

    re = np.c_[point, dist]
    print(f're = \n{re}\n')


def np_row_col1():
    """
    In Python, a single vector is represented in the form of (2,) and a collection of multiple
    vetors such as a_col is a matrix expressed as (2, 1) => (# of rows, # of columns).

    Bracket ([]): Refers to the axis
    The number of square brackets within the obje t determines the dimension
    """
    header('NP row vs column')
    a_row = np.array([1, 2])  # row vector
    a_col = np.array([[1], [2]])  # column vector
    print(f'{a_row = }\n{a_col = }\n')

    print(f'Dimension of a_row: {a_row.ndim}, Shape of a_row: {a_row.shape}')
    print(f'Dimension of a_col: {a_col.ndim}, Shape of a_col: {a_col.shape}')


def np_reshape_transpose():
    """
    In np.reshape() function, the number of rows as an argument is -1. this means that the value is
    automatically assigned based on the value of the other argument, the column. In the following cases,
    the number of rows is automatically adjusted based on the number of column 2.

    This is different from the transpose
    """
    arr = np.array([[5., 3., -2., -3.], [3., -4., -4., 5.]])
    print(f'arr = \n{arr}\n')
    print(f'Dimension of arr: {arr.ndim}')
    print(f'Shape of arr: {arr.shape}\n')

    print(f'Reshaping the arr: \n{arr.reshape(-1, 2)}')
    print(f'Transpose of arr: \n{arr.T}\n')


def np_vector_ops():
    header('NP Vector Operations')
    a = np.array([10, 15])
    b = np.array([8, 2])
    c = np.array([1, 2, 3])

    print(f'a = {a}')
    print(f'-a = {-a}')
    print(f'b = {b}')
    print(f'-b = {-b}')
    print(f'c = {c}\n')

    print(f'a + b = {a + b}')
    print(f'a - b = {a - b}')
    print(f'a * b = {a * b}')
    print(f'a / b = {a / b}\n')

    try:
        print(f'a - c = {a - c}\n')
    except ValueError:
        print('a - c raise error!')
        print('a and c does not have the same shape')


if __name__ == '__main__':
    # NP Concatenate (np.c_)
    np_concat()

    # NP row vs column
    np_row_col1()

    # NP reshape and transpose
    np_reshape_transpose()

    # NP Vector operations
    np_vector_ops()
