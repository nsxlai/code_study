"""
Create a singleton class
"""


class Singleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls.data = {}
        return cls._instance


if __name__ == '__main__':
    a = Singleton()
    b = Singleton()
    print(f'a == b ? {a == b}')
    a.data.setdefault('test01', 'EEPROM programming')
    print(f'{b.data = }')
    print(f'{id(a) = }, {id(b) = }')
