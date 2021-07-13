import h5py

FILENAME = 'REL_TESTING_Tmin_Vmin.h5'


def dir_list(df_obj):
    if len(df_obj) == 0:
        return df_obj.name

    print(f'{list(df_obj)}')
    try:
        for data in list(df_obj):
            print(f'Exploring {data} ...')
            try:
                dir_list(df_obj.get(data))
            except AttributeError as e:
                """ Dataset does not have get method; not a dict """
                print(e)
    except TypeError:
        print('Unable to display content')


if __name__ == '__main__':
    f = h5py.File(FILENAME, 'r')
    print(f'{f = }')
    print(f'{f.get("/") = }')
    print(f'{list(f.get("/")) = }')
    print(f'{list(f.get("/").get("bp001")) = }')
    level_01 = list(f.get("/").get("bp001"))
    for subgroup in level_01:
        print(f'{subgroup = }')

    dir_list(f)




