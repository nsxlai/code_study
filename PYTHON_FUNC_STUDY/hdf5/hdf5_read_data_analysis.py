import h5py
from pprint import pprint


if __name__ == '__main__':
    h5_filename = 'hdf5_read_example.h5'
    h = h5py.File(h5_filename, 'r')

    print(f'{h.keys() = }')  # Only Fennec_20210310 key present; <KeysViewHDF5 ['fennec_20210310']>
    test_level_1 = list(h.keys())[0]
    print(f'{test_level_1 = }')
    print(f'{h[test_level_1] = }')
    tests = list(h[test_level_1].keys())
    print(f'{tests = }')  # list of tests under the directory
    output_data = {}

    for test in tests:
        output_data[test] = list(h[test_level_1][test][()])
        # h[test_level_1][test][()] is the same as h[test_level_1][test].value but .value is depreciated
    h.close()

    pprint(f'{output_data = }')
