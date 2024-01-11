"""
This is a pseudo code; only containing abstract level coding
"""
# import paramiko
# import toml
import urllib
from abc import ABC, abstractmethod
from collections import OrderedDict


__AUTHOR__ = 'Ray Lai'
__VERSION__ = '0.5.0'


class SensorError(Exception):
    pass


def ssh_connect():
    print('Initiating SSH connection...')
    global ssh_client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOST, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)


def rest_api_call(api_call: str):
    """
    Function handling generic REST API call and return error if present
    """
    pass  # TODO add concrete coding


def func_select(enable: str):
    def wrapper(func):
        def inner(*args):
            data = func(*args)
            return data
        return inner
    return wrapper


class SensorTest(ABC):
    @abstractmethod
    def __init__(self):
        pass
    @abstractmethod
    def ping_i2c(self) -> str:
        pass

    @abstractmethod
    @property
    def sensor_value(self):
        pass

    @abstractmethod
    def compare_ext_sensor(self) -> bool:
        pass


class LightSensor(SensorTest):
    def __init__(self):
        ...

    def ping_i2c(self) -> str:
        ...

    @property
    def sensor_value(self):
        ...

    def compare_ext_sensor(self) -> bool:
        ...


class MotionSensor(SensorTest):
    def __init__(self):
        ...

    def ping_i2c(self) -> str:
        ...

    @property
    def sensor_value(self):
        ...

    def compare_ext_sensor(self) -> bool:
        ...


class TemperatureSensor(SensorTest):
    def __init__(self):
        ...

    def ping_i2c(self) -> str:
        ...

    @property
    def sensor_value(self):
        ...

    def compare_ext_sensor(self) -> bool:
        ...


class EEPROM:
    def __init__(self):
        ...

    def read_value(self):
        ...

    def write_value(self):
        ...

    def write_protect(self, enable: bool = True):
        ...
    

class EthernetTraffic:
    def __init__(self):
        ...

    def init_traffic(self):
        ...

    def capture_traffic(self):
        ...

    def analyze_traffic(self):
        ...


class POE:
    def __init__(self):
        ...

    def read_dut_poe_value(self):
        ...

    def read_switch_poe_value(self):
        ...


class MCUStress:
    def __init__(self):
        ...

    @property
    def get_mcu_temp_sensor_values(self):
        ...

    def set_mcu_utilization(self):
        ...

    def mcu_dram_test(self):
        ...


def main():
    complete_test_seq = OrderedDict([
        ['light_sensor_test', [LightSensor, True]],
        ['motion_sensor_test', [MotionSensor, True]],
        ['temp_sensor_test', [TemperatureSensor, True]],
        ['eeprom_test', [EEPROM, True]],
        ['ethernet_traffic_test', [EthernetTraffic, False]],
        ['ethernet_poe_test', [POE, False]],
        ['mcu_stress_test', [MCUStress, False]],
        ['dram_test', [MCUStress, False]],
    ])

    test_seq = []
    for key, value in complete_test_seq.items():
        if value[1] is True:
            test_seq.append(test_seq[key][0](enable=True))


if __name__ == '__main__':
    main()
