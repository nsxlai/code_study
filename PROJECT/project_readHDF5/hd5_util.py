import h5py


if __name__ == '__main__':
    min_file = 'REL_TESTING_04-09-2020_11_54_00_Tmin_Vmin.h5'
    max_file = 'REL_TESTING_04-09-2020_11_56_01_Tmin_Vmax.h5'
    with h5py.File(min_file, 'r') as f:
        data = f.__dict__

    print(f'{data = }')
