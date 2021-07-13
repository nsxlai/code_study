# Example Python program that creates a hierarchy of groups
# and datasets in a HDF5 file using h5py
# Source1: https://pythontic.com/hdf5/h5py/create_group
# Source2: https://docs.h5py.org/en/stable/quick.html
import h5py
import random
import numpy.random


if __name__ == '__main__':
    # Create a HDF5 file
    FileName = "hdf5_example.h5"
    File = h5py.File(FileName, "w")

    # Create a group under root
    grp1 = File.create_group("Group1")
    grp2 = grp1.create_group("Group2")
    grp3 = grp2.create_group("Group3")

    # Use POSIX path to create a hierarchy of group under root
    grp4 = File.create_group("/GroupA/GroupB/GroupC")

    # Use dictionary notation to create a dataset inside a group
    grp4["D1"] = 1

    # Create another dataset inside the same group
    datasetShape = (10, 2)
    d2 = grp4.create_dataset("D2", datasetShape)
    s3 = grp3.create_dataset(name='a3', shape=datasetShape, dtype=int)

    print(f'{File.keys() = }')
    # Print the groups
    print(f'{File["/"] = }')
    print(f'{grp1 = }')
    print(f'{list(grp1) = }')
    print(f'{grp2 = }')
    print(f'{grp2.name = }')
    print(f'{File[grp2.name] = }')  # same as print(f'{grp2 = }')
    print(f'{grp4["D2"].name = }')
    print(f'{grp3 = }')
    print(f'{grp4 = }')
    print(f'{list(grp4) = }')
    print(f'{grp4["D1"] = }')
    print(f'{grp4["D1"].parent = }')
    print(f'{grp4["D2"] = }')
    print(f'{grp4["D2"].parent = }')

    # Add value to the D2 dataset
    for a in range(d2.shape[0]):
        for b in range(d2.shape[1]):
            d2[a, b] = numpy.random.uniform(1, 1000, 1)[0]

    print("Data from d2:")
    # Read value from the dataset
    for x in range(10):
        for y in range(2):
            if y == 0:
                print(f'{d2[x, y] = }', end='\t\t')
            else:
                print(d2[x, y])

    # Display few items
    print(list(File.keys()))
    d2.attrs['metadata'] = "sample"
    print(f'{d2[()] = }')  # same as d2.value (deprecated); show the value of the array data

    '''
    d2 = grp4.create_dataset("D2", datasetShape)
    For d2 (dataset variable), unable to find to correlation between D2 and d2
    grp4['D2'][()] or grp4['D2'].value (deprecated) will show the dataset, like d2[()]
    
    grp4['D2'] does not have an attribute contains 'd2'
    '''
    for val in grp4:
        print(f'{val = }')