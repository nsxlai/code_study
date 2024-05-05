class Blue:
    _shared_state = {}

    def __init__(self):
        self.__dict__ = self._shared_state


class example:
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return 'example representation'


if __name__ == '__main__':
    a = example(100)
    print(a)
    print(str(a))
    print(repr(a))

    b = Blue(test='test001')
    print(b)