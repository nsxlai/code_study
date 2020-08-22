if __name__ == '__main__':
    list1 = ['t01', 't02', 't05', 't10', 't06']
    list2 = ['t10', 't20', 't04', 't05', 't01', 't06']

    # to find the common items between the 2 lists:
    print(f'{set(list1).intersection(set(list2)) = }')
    print(f'{set(list1) & set(list2) = }')
