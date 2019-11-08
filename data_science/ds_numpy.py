# code is sourced from Medium.com titled: First Step in Data Science with Python - NumPy
from random import randint
import numpy as np


no_of_items = 10
lower_limit = 5
upper_limit = 25


# Traditional way of generating random list
value_01 = [randint(lower_limit, upper_limit) for _ in range(no_of_items)]
print(f'Random generated list from random lib: {value_01}')


# Numpy random array
np.random.seed(0)
value_02 = np.random.randint(lower_limit, upper_limit, no_of_items)
print(f'Random generated numpy integer array: {value_02}')

# value_03 = np.random.rand(lower_limit, upper_limit, no_of_items)
# print(f'Random generated numpy float array: {value_03}')
#
# value_04 = np.random.rand(lower_limit, upper_limit, no_of_items)
# print(f'Random generated numpy float array: {value_04}')


print(f'Numpy array dimension: {value_02.ndim}')
print(f'Numpy array size:      {value_02.size}')
print(f'Numpy array dtype:     {value_02.dtype}')
print(f'Numpy array shape:     {value_02.shape}')
print()


no_of_rows = 5
no_of_columns = 2
containers = value_02.reshape(no_of_rows, no_of_columns)
print(f'Reshaped numpy array (containers): {containers}')
print(f'Containers dimension: {containers.ndim}')
print(f'Containers size:      {containers.size}')
print(f'Containers dtype:     {containers.dtype}')
print(f'Containers shape:     {containers.shape}')
print()

# Build 5 cylindrical containers from the container numpy array
radius = containers[:, 0]  # First element of the 2D arrays
height = containers[:, 1]

# Method 1:
volume = np.pi*(radius**2)*height
total_volume = volume.sum()
print(f'Containers volume:       {volume}')
print(f'Containers total volume (method 1): {total_volume}')


# Method 2:
# The dot product works here because both radius_squared and height are one dimensional
# For 2D array, one of the array must use np.transpose() method
radius_squared = np.square(radius)
dot_product = np.dot(radius_squared, height)
total_volume_by_dot_product = np.pi*dot_product
print(f'Containers total volume (method 2): {total_volume_by_dot_product}')
print()


max_volume = volume.max()
index_of_max_volume = volume.argmax()
min_volume = volume.min()
index_of_min_volume = volume.argmin()
print(f'Max volume is {max_volume:.3f} with index {index_of_max_volume}')
print(f'Min volume is {min_volume:.3f} with index {index_of_min_volume}')
print()


volume_mean = np.mean(volume)
volume_median = np.median(volume)
volume_std_dev = np.std(volume)
print(f'Volume mean value: {volume_mean}')
print(f'Volume median value: {volume_median}')
print(f'Volume standard deviation: {volume_std_dev}')





