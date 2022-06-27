from singleton_04_04_module import s1


if __name__ == '__main__':
    g1 = s1
    g2 = s1

    print(f'{id(g1) = }')
    print(f'{id(g2) = }')

    if id(g1) == id(g2):
        print('g1 object is the same object as g2')
