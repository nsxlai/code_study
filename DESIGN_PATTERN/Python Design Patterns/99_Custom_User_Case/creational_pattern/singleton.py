class Singleton1:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance


class Singleton2:
    _instance = None

    def __new__(self):
        if not self._instance:
            self._instance = super().__new__(self)
            self.y = 10
        return self._instance


if __name__ == '__main__':
    a = Singleton1()
    b = Singleton1()
    print(f'{a = }')
    print(f'{b = }')
    print(f'{a == b = }')

    c = Singleton2()
    d = Singleton2()
    print(f'{c = }')
    print(f'{d = }')
    print(f'{c == d = }')

    print(f'{c.y = }')
    print(f'{d.y = }')
    c.y += 20
    print(f'{c.y = }')
    print(f'{d.y = }')
