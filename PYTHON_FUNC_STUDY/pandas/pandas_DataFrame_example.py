import pandas as pd
import numpy as np


def df_example1():
    """ Create DataFrame with individual component """
    dates = pd.date_range('today', periods=6)
    print(f'{dates = }')

    num_arr = np.random.rand(6, 4)  # 6 rows and 4 columns
    print(f'{num_arr = }')

    columns = ['A', 'B', 'C', 'D']

    df1 = pd.DataFrame(num_arr, index=dates, columns=columns)
    print(f'df1 = \n{df1}\n')


def df_example2():
    """ Create DataFrame with Dictionary """
    data = {'animal': ['cat', 'cat', 'snake', 'dog', 'dig', 'cat', 'snake', 'cat', 'dog', 'dog'],
            'age': [2.5, 3, 0.5, np.nan, 5, 2, 4.5, np.nan, 7, 3],
            'visits': [1, 3, 2, 3, 2, 3, 1, 1, 2, 1],
            'priority': ['yes', 'yes', 'no', 'yes', 'no', 'no', 'no', 'yes', 'no', 'no'],
            }
    labels = 'a b c d e f g h i j'.split()

    df2 = pd.DataFrame(data, index=labels)
    print(f'df2 = \n{df2}\n')


def df_example3():
    """ Create DataFrame with Dictionary """
    data = {'A': [1, 2, 3, 4],
            'B': pd.Timestamp('20221030'),
            'C': pd.Series(1, index=list(range(4)), dtype='float32'),
            'D': np.array([5]*4, dtype='int32'),
            'E': pd.Categorical(['True', 'False', 'True', 'False']),
            'F': 'Pandas'}

    df3 = pd.DataFrame(data)
    print(f'df3 = \n{df3}\n')


if __name__ == '__main__':
    # df_example1()
    # df_example2()
    df_example3()
