"""
Create the factory design pattern from the example code below
"""
class TestA:
    def __init__(self, name):
        self.__test_name = name
        self.__test_sequence = ['A', 'B', 'C']
        self.__test_result = ''

    def execute(self):
        print(f'Executing test {self.__test_sequence}')
        self.__test_result = 'PASS'

    @property
    def test_result(self):
        return self.__test_result


class TestB:
    def __init__(self, name):
        self.__test_name = name
        self.__test_sequence = ['B', 'A', 'A', 'C', 'D']
        self.__test_result = ''

    def execute(self):
        print(f'Executing test {self.__test_sequence}')
        self.__test_result = 'PASS'

    @property
    def test_result(self):
        return self.__test_result