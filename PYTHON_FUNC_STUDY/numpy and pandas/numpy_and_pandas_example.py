import numpy as np
import pandas as pd
from math import sqrt


if __name__ == '__main__':
    point = np.array([[5, 3], [3, -4], [-2, -4], [-3, 5]])
    print(f'{point = }')

    dist = [sqrt(point[i, 0]**2 + point[i, 1]**2) for i in range(4)]
    print(f'{dist}')

    re = np.c_[point, dist]
    print(f'{re = }')
    re1 = pd.DataFrame(re)
    re1.columns = ['x', 'y', 'distance']
    re1.index = ['b', 'g', 'r', 'k']
    print(f'{re1}')