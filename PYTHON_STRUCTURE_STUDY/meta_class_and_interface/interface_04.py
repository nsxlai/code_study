class base_util:
    def util_A(self, p: int):
        raise NotImplemented

    def util_B(self, k: int):
        raise NotImplemented


class security_util(base_util):
    """ Implement both interface methods """
    def util_A(self, p: int):
        return p + 1

    def util_B(self, k: int):
        return k + 10


class incomplete_util(base_util):
    """ Did not implement util_A but run time engine won't give an error"""
    def util_B(self, k: int):
        return k + 100


if __name__ == '__main__':
    su = security_util()
    iu = incomplete_util()

    try:
        print(f'{su.util_A(9) = }')
        print(f'{iu.util_B(50) = }')
        print(f'{iu.util_A(50) = }')  # Will give NotImplemented error
    except NotImplemented and TypeError:
        print('Did not completely implement the required interface method')
