# source: https://towardsdatascience.com/dont-use-recursion-in-python-any-more-918aad95094c


def outer():
    x = 1

    def inner():
        nonlocal x
        print(f'x in outer function (before modifying): {x}')
        x += 1
        print(f'x in outer function (after modifying): {x}')
    return inner


if __name__ == '__main__':
    f = outer()
    for i in range(5):
        print(f'Run {i + 1}')
        f()
        print('\n')
