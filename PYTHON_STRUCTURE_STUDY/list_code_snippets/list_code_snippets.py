"""
source: https://python.plainenglish.io/10-python-snippets-i-use-everyday-4d3f58de841d
"""


def string_case():
    """Change string case (upper/lower/title)"""
    print('Change string case', '-' * 20)
    my_string = "sTrangECaSE"
    print('Standard:', my_string)
    my_string_lower = my_string.lower()
    print('Lower:', my_string_lower)
    my_string_upper = my_string.upper()
    print('Upper:', my_string_upper)
    my_string_title = my_string.title()
    print('Title:', my_string_title)
    my_string_capital = my_string.capitalize()
    print('Capitalize:', my_string_capital)


def string_split_and_join():
    """Split a string and join it back"""
    print('Split a string and join it back', '-' * 20)
    my_string = "This is a string"
    print("Original string:", my_string)
    my_string_list = my_string.split()
    my_string_list = [el.title() for el in my_string_list]
    my_string = " ".join(my_string_list)
    print("Modified String:", my_string)


def list_flatting():
    """ List flattening"""
    print('List flattening', '-' * 20)
    list_of_lists = [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]]
    print('Input:', list_of_lists)
    flattened_list = [item for sublist in list_of_lists for item in sublist]
    print('Output:', flattened_list)


def get_list_unique_element():
    """ Get unique elements from list"""
    print('Get unique elements from list', '-' * 20)
    list_duplicates = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'a', 'a', 'c', 'd', 'e', 'l', 'g', 'z', 'i']
    print('Duplicates:', list_duplicates)
    unique_list = list(set(list_duplicates))
    print('Uniques:', unique_list)
    # If you need to sort the list
    print('Sorted Uniques:', sorted(unique_list))


def merge_list_into_dict_1():
    """ Merge two list into a dictionary"""
    print('Merge two list into a dictionary', '-' * 20)
    list_a = ['a', 'b', 'c']
    list_b = [1, 2, 3]
    print(f'{list_a = }, {list_b = }')

    # list_a is the key and list_b is the value
    out_dict1 = dict(zip(list_a, list_b))
    print(f'{out_dict1 = }')

    # list_b is the key and list_a is the value
    out_dict2 = dict(zip(list_b, list_a))
    print(f'{out_dict2 = }')


def merge_list_into_dict_2():
    """ Merge two list into a dictionary"""
    print('Merge two list of uneven length into a dictionary', '-' * 20)
    from itertools import zip_longest
    list_a = ['a', 'b', 'c']
    list_b = [1, 2, 3, 4, 5]
    out_dict1 = dict(zip_longest(list_a, list_b))
    print(f'{out_dict1 = }')

    list_c = ['a', 'b', 'c', 'd', 'e']
    list_d = [1, 2, 3]
    out_dict2 = dict(zip_longest(list_c, list_d))
    print(f'{out_dict2 = }')


def merge_dict():
    """ Example from RealPython """
    print('Merging 2 dictionaries', '-' * 20)
    x = {'a': 1, 'b': 2}
    y = {'b': 3, 'c': 4}
    z = {**x, **y}
    print(f'{x = }, {y = }')
    print(f'{z = }')


def sort_list_of_dict_with_key():
    """ Sort a list of dictionaries by a key"""
    print('Sort a list of dictionaries by a key', '-' * 20)
    people = [
        {'name': 'John', 'height': 90},
        {'name': 'Mary', 'height': 160},
        {'name': 'Isla', 'height': 80},
        {'name': 'Sam', 'height': 75},
    ]
    print(f'{people = }')
    sorted_people = sorted(people, key=lambda k: k['height'])
    print(f'{sorted_people = }')


def sort_dict_by_key_and_value():
    print('Sort a dictionaries by key and value', '-' * 20)
    people = {3: "Jim", 2: "Jack", 4: "Jane", 1: "Jill"}
    print(f'{people = }')
    # Sort by key
    key_sort = dict(sorted(people.items()))
    print(f'{key_sort = }')
    # {1: 'Jill', 2: 'Jack', 3: 'Jim', 4: 'Jane'}

    # Sort by value
    value_sort = dict(sorted(people.items(), key=lambda item: item[1]))
    print(f'{value_sort = }')
    # {2: 'Jack', 4: 'Jane', 1: 'Jill', 3: 'Jim'}


def sort_list_by_list():
    """ Sort a list based on another list"""
    print('Sort a list based on another list', '-' * 20)
    list_a = ['a', 'b', 'c']
    list_b = [2, 0, 1]
    print('Original List:', list_a)
    ordered_list_a = [list_a[i] for i in list_b]
    print('Ordered List:', ordered_list_a)


def get_most_freq_value_from_list():
    """ Get most frequent value from a list"""
    print('Get most frequent value from a list', '-' * 20)
    list_a = ['a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'c', 'a', 'b', 'b', 'a', 'b', 'c', 'b', 'b', 'c', 'a', 'b', 'c']
    print(f'{list_a = }')
    print('Most frequent value:', max(set(list_a), key=list_a.count))


def palindrome():
    print('palindrome', '-' * 20)
    palindrome_string = "racecar"
    is_palindrome = palindrome_string == palindrome_string[::-1]
    print("Is a palindrome:", is_palindrome)


if __name__ == '__main__':
    string_case()
    string_split_and_join()
    list_flatting()
    get_list_unique_element()
    merge_list_into_dict_1()
    merge_list_into_dict_2()
    merge_dict()
    sort_list_of_dict_with_key()
    sort_dict_by_key_and_value()
    sort_list_by_list()
    get_most_freq_value_from_list()
    palindrome()
