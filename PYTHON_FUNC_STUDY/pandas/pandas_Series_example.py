import pandas as pd
import numpy as np


if __name__ == '__main__':
    # Create a Series (1D data structure)
    arr = [0, 1, 2, 3]
    s1 = pd.Series(arr)
    print(f's1 = \n{s1}\n')

    # Set index of a Series
    n = np.random.randn(5)  # create a random array
    s2_index = 'a b c d e'.split()
    s2 = pd.Series(n, index=s2_index)
    print(f's2 = \n{s2}\n')

    # Create Series from a dictionary
    d = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
    s3 = pd.Series(d)
    print(f's3 = \n{s3}\n')

    # Alter Series index
    print(f's2 index = {list(s2.index)}')
    s2.index = 'M N O P Q'.split()
    print(f'Changing s2 index = \n{s2}\n')

    # Slicing
    print('---- Slicing ------')
    print(f's1 = \n{s1}\n')
    print(f's1[:-1] = \n{s1[:-1]}\n')
    print(f's1[-2:] = \n{s1[-2:]}\n')

    # Appending Series
    print('---- Appending ------')
    print(f's1 = \n{s1}\n')
    print(f's3 = \n{s3}\n')
    # s4 = s1.append(s3)  # FutureWarning: The series.append method is deprecated and will be removed
    #                       from pandas in a future version. Use pandas.concat instead.
    s4 = pd.concat([s1, s3])
    print(f's4 = \n{s4}\n')

    # Dropping a row
    print('---- Dropping --------')
    s4.drop([2, 'd'], inplace=True)  # if inplace is not true (default inplace = False), the drop will not modify the original Series and
                                     # only output the possible dropped state
    print(f's4 = \n{s4}\n')

    # Add/substract/multiply/divide
    print('---- Add/substract/multiply/divide --------')
    arr1 = [0, 1, 2, 3, 4, 5, 6, 7]
    arr2 = [6, 7, 8, 9, 5]

    s5 = pd.Series(arr1)
    s6 = pd.Series(arr2)

    print(f'{s5.add(s6) = }')
    print(f'{s5.sub(s6) = }')
    print(f'{s5.mul(s6) = }')
    print(f'{s5.div(s6) = }')

    s7 = s5.mul(s6)
    print(f'{s7.median() = }')
    print(f'{s7.max() = }')
    print(f'{s7.min() = }')
