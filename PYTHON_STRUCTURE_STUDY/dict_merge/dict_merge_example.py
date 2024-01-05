
def dict_merge_method1(*dict_src):
    cities = {}
    for city_dict in dict_src:
        for city, country in city_dict.items():
            cities[city] = country
    print('Method 1: ', cities)


def dict_merge_method2(c1, c2, c3):
    cities = c1 | c2 | c3
    print('Method 2: ', cities)


def dict_merge_method3(c1, c2, c3):
    c1 |= c2 | c3
    print('Method 3: ', c1)


def dict_merge_method4():
    """
    Merging 2 dictionaries. This method will work only if both dictionary has no overlapping keys. If there are
    overlapping keys, the keys from the first dict will be overwritten by the second dict
    """
    c1 = {'a': 3, 'b': 5, 'c': 10}
    c2 = {'b': 20, 'c': 50, 'd': 60}
    c3 = {**c1, **c2}
    print(f'Original dict c1: {c1}')
    print(f'Original dict c2: {c2}')
    print(f'Merged dict Method 4: {c3}')


if __name__ == '__main__':
    cities_us = {'New York City': 'US', 'Los Angeles': 'US'}
    cities_uk = {'London': 'UK', 'Birmingham': 'UK'}
    cities_jp = {'Tokyo': 'JP'}

    dict_merge_method1(cities_us, cities_uk, cities_jp)
    dict_merge_method2(cities_us, cities_uk, cities_jp)
    dict_merge_method3(cities_us, cities_uk, cities_jp)

    dict_merge_method4()
