"""
source: geeksforgeeks.org
"""


class Product:
    def __init__(self):
        print('Instance created')

    def __call__(self, a: int, b: int) -> int:
        return a * b


if __name__ == '__main__':
    p = Product()
    print(f'{p(10, 20) = }')
