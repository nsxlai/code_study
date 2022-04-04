"""
source: https://medium.com/@vlad.bashtannyk/why-python-developers-should-use-staticmethod-and-classmethod-d5fe60497f23

This example demonstrates the inheritance with classmethod vs staticmethod
"""
class Supermarket:
    product_price = {"Milk": 1}
    def __init__(self, product, best_before):
        self.best_before = "2022-05-18"
        self.product = "Milk"

    @staticmethod
    def add_product_staticmethod(product, best_before):
        return Supermarket(product, best_before)

    @classmethod
    def add_product_classmethod(cls, product, best_before):
        return cls(product, best_before)


class GroceryStore(Supermarket):
    product_price = {"Milk": 2}


if __name__ == '__main__':
    grocery1 = GroceryStore.add_product_staticmethod("Bread", "2022-06-05")
    print(f'staticmethod: {isinstance(grocery1, GroceryStore) = }')

    grocery2 = GroceryStore.add_product_classmethod("Apple", "2022-06-10")
    print(f'classmethod: {isinstance(grocery2, GroceryStore) = }')
