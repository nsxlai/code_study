# source: https://www.programiz.com/python-programming/property
# Using @property decorator
class Celsius:
    def __init__(self, temperature=0):
        self.temperature = temperature

    def to_fahrenheit(self):
        return (self.temperature * 1.8) + 32

    @property
    def temperature(self):
        print("Getting value...")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        print("Setting value...")
        if value < -273.15:
            raise ValueError("Temperature below -273 is not possible")
        self._temperature = value

    @temperature.deleter
    def temperature(self):
        self._temperature = None


if __name__ == '__main__':
    human = Celsius(37)
    print(f'{human.temperature = }')
    print(f'{human.to_fahrenheit() = }')
    print(dir(human)[-3:])  # showing both temperature at property attribute and _temperature as private attribute
    coldest_thing = Celsius(-300)

    del human.temperature
    print(f'{human.temperature = }')
