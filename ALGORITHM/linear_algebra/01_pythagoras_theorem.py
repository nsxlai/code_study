"""
source: from the book "Linear Algebra Coding with Python", section 1.1
"""
import numpy as np
import pandas as pd
from math import sqrt
# import numpy.linalg as la


def distance(pt: list) -> float:
    # return (pt[0]**2 + pt[1]**2)**0.5
    return sqrt(pow(pt[0], 2) + pow(pt[1], 2))


if __name__ == '__main__':
    point = np.array([[5, 3], [3, -4], [-2, -4], [-3, 5]])
    print(f'point = \n{point}\n')

    d = [distance(point[i]) for i in range(len(point))]
    re = np.c_[point, d]  # concatenate d into the point NP array
    re1 = pd.DataFrame(re)
    re1.columns = ['x', 'y', 'distance']
    re1.index = ['b', 'g', 'r', 'k']
    print(f're1 = \n{re1}\n')
