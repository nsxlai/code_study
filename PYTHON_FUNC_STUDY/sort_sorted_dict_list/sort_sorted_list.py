from copy import deepcopy


if __name__ == '__main__':
    sample_list = ['Banana', 'Apple', 'Orange', 'Carrot', 'Apricot', 'Melon']
    sample_dict = {'Banana': 3, 'Apple': 6, 'Orange': 10, 'Carrot': 4, 'Melon': 1, 'Apricot': 5}

    print(' sorted() '.center(80, '='))
    print(f'{sample_list = }')
    print(f'{sorted(sample_list) = }')
    print(f'{sorted(sample_list, reverse=True) = }')
    print(f'{sorted(sample_list, key=len) = }')
    print()

    print(' reversed() '.center(80, '='))
    print(f'{sample_list = }')
    print(f'{list(reversed(sample_list)) = }')  # Reversed function is not in-place
    print(f'{sample_list = }')
    print()

    print(' sort() '.center(80, '='))
    print(f'{sample_list = }')
    temp_list = deepcopy(sample_list)
    print(f'{sample_list.sort() = }')  # sort is in-place and update (mutate) the list; output None
    print(f'{sample_list = }')  # Output the sort result; the original list is modified
    print(f'{sample_list.sort(reverse=True) = }')
    print(f'{sample_list = }')  # Output the sort result; the original list is modified
    # print(f'{temp_list = }')
    sample_list = temp_list
    print()

    print(' sort() with key '.center(80, '='))
    sample_list1 = [(1, 2), (4, 3), (1, 1)]


    def sortSecond(lst):
        return lst[1]
    print(f'{sample_list1.sort(key=sortSecond) = }')
    print(f'{sample_list1 = }')




