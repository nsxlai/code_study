from datetime import datetime, date
from functools import wraps
from time import sleep
from typing import Callable


SEL = 0


def switch_cable():
    print('Switch the cable connection...')
    sleep(2)


def power_on_uut():
    print('Power on the UUT...')
    sleep(5)


def reboot_uut():
    print('Reboot the UUT...')
    sleep(5)


def disable_diag():
    print('Disable the diagnostic interference...')
    sleep(2)


def get_datetime_str():  # Adding this here until Stoa is requirement
    """Get the date time string : YYYYMMDDHHMMSS.
    """
    date_object = date.today()
    current_date = str(date_object).replace('-', '')

    time_object = datetime.now()
    current_time = time_object.strftime("%H%M%S")

    datetime_str = (str(current_date) + str(current_time))
    print(f'Date time string: {datetime_str}')


def uut_config_01():
    print('Configure the UUT; configuration 01...')
    sleep(2)


def uut_config_02():
    print('Configure the UUT; configuration 02...')
    sleep(2)


def init_system():
    print('Perform system initialization before testing the UUT...')
    sleep(3)


def reset_system():
    print('Reset the system back to the original config')
    sleep(3)


def main_test():
    ''' The Main test is part of the main sequence '''
    print('Perform main test...')
    sleep(5)


def display_test_result():
    print('Test Result: PASSED')
    sleep(1)


def sequence_select(sel: int):
    def func_input(func: Callable):
        @wraps(func)
        def sequence():
            """ Choose sequence 01 or 02 """
            if sel == 0:
                sequence_00()
            elif sel == 1:
                sequence_01()
            elif sel == 2:
                sequence_02()
            return
        return sequence
    return func_input


@sequence_select(sel=SEL)
def main_sequence():
    pass


class Sequencer:
    def __init__(self):
        self._objects = {}

    def register_sequence(self, idx: int, obj: Callable):
        """Register an object"""
        print(f'Registering {obj.__name__} in index {idx}')
        self._objects[idx] = obj

    def sequence(self, idx):
        """ Select the index to execute the sequence from the dictionary """
        self._objects[idx]()


def sequence_00():
    print('Test Sequence 00')
    get_datetime_str()
    init_system()
    power_on_uut()
    uut_config_01()
    main_test()
    display_test_result()


def sequence_01():
    print('Test Sequence 01')
    get_datetime_str()
    init_system()
    power_on_uut()
    uut_config_01()
    main_test()
    switch_cable()
    sleep(3)
    main_test()
    reset_system()
    display_test_result()


def sequence_02():
    print('Test Sequence 02')
    get_datetime_str()
    init_system()
    reboot_uut()
    uut_config_02()
    main_test()
    switch_cable()
    reboot_uut()
    uut_config_02()
    main_test()
    reset_system()
    display_test_result()


if __name__ == '__main__':
    # Decorator pattern for use SEL to select test sequences
    # main_sequence()

    # Use prototype pattern
    seq = Sequencer()
    seq.register_sequence(0, sequence_00)
    seq.register_sequence(1, sequence_01)
    seq.register_sequence(2, sequence_02)
    seq.sequence(2)

