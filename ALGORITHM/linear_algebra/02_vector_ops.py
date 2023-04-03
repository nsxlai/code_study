"""
source: from the book "Linear Algebra Coding with Python, section 1.1
"""
import numpy as np
import pandas as pd


if __name__ == '__main__':
    a = np.array([10, 15])
    b = np.array([8, 2])

    print(np.dot(a, b))