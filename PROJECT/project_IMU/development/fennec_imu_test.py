from genericpath import isfile
from win32com.client.dynamic import Dispatch
from win32com.client import VARIANT
import pythoncom
import os
import codecs
from typing import Any, List
import argparse
from time import sleep, time
import subprocess
import platform
import sys
import ctypes


__AUTHOR__ = 'ray.lai@getcruise.com'
__version__ = '1.0.6'

# SigmaStudio Files
SigmaStudioServer = 'Analog.SigmaStudioServer.SigmaStudioServer'
project_file_path = 'C:\\Users\\hardware R&D\\Documents\\Fennec_EV_Test_v4'
project_file_name = 'FENNEC_A2B_1Node_24bit_R1_EV_EEPROM_Programming.dspproj'
project_file = os.path.join(project_file_path, project_file_name)


# Hardware constants
ic_name = VARIANT( pythoncom.VT_BYREF | pythoncom.VT_BSTR, "IC 1")
masterAddress = 0x68
busAddress = 0x69
addrwidth = 1
writeNumberBytes = 4
readdata = bytearray(8)
readdata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, readdata)


def hex_to_ascii(hex_str: str) -> str:
    binary_str = codecs.decode(hex_str[2:], 'hex')  # Remove the leading '0x'
    ascii_str = str(binary_str, 'utf-8')
    return ascii_str


def server_init(verbose: bool = False) -> Any:
    """ This function will link/compile/download the DSP project file code to Fennec. If the project code is not
        loaded, this function will load the code from the specified project_file path. Will retry only once before
        manually raise the error to exit the program
    """
    server = Dispatch(SigmaStudioServer)
    if server.compile_project:
        if verbose:
            print('Fennec chain initialized...')
    else:
        if verbose:
            print('Fennec chain is unable to initialize; attempt to load the DSP project file...')
        server.open_project(project_file)
        if server.compile_project:
            if verbose:
                print('Fennec chain initialized...')
        else:
            raise ValueError('Fennec chain is unable to initialize; please debug the HW/SW setup...')
    return server


def extract_data_points(filename: str) -> List:
    os_running = platform.system()
    if os_running == 'Windows':
        custom_slice = slice(8, 57)  # Windows version of the hexdump is not the same as the Linux version of the hexdump
    else:
        custom_slice = slice(10, 57)  # Linux and MAC has the same hexdump utility
    p = subprocess.Popen(f'hexdump -C {filename}', shell=True, stdout=subprocess.PIPE)
    data = []
    for line in p.stdout:
        temp = line.decode(encoding='utf-8', errors='ignore')  # encode with utf-8
        temp = temp[custom_slice].replace(' ', '')  # remove the space between each byte, for 4 bytes (1 line)
        data.append(temp)
    return data


def time_elapse(func):
    def wrapper_func(*args, **kwargs):
        start_time = time()
        func(*args, **kwargs)
        end_time = time()
        print(f'Time elapsed: {end_time-start_time}')
        return
    return wrapper_func


@time_elapse
def eeprom_data_write(server: Any, data: List) -> None:
    node = 0
    writeNumberBytes = 16
    
    writedata_list = data[:3430]  # 13720/4 = 3430
    chipAddress = 0x50
    for index, data_point in enumerate(writedata_list):
        writedata = bytearray(codecs.decode(data_point, 'hex'))
        writedata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, writedata)
        writeAddress = index * writeNumberBytes
        print(f'EEPROM {hex(chipAddress)}: Writing {data_point} to address {writeAddress:04x}')
        server.A2B_SLAVE_PERIREGISTER_WRITE(ic_name, masterAddress, busAddress, node, chipAddress, writeAddress, addrwidth, writeNumberBytes, writedata_v)

    writedata_list = data[3430:]  # 13720/4 = 3430
    chipAddress = 0x51
    for index, data_point in enumerate(writedata_list):
        writedata = bytearray(codecs.decode(data_point, 'hex'))
        writedata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, writedata)
        writeAddress = index * writeNumberBytes
        print(f'EEPROM {hex(chipAddress)}: Writing {data_point} to address {writeAddress:04x}')
        server.A2B_SLAVE_PERIREGISTER_WRITE(ic_name, masterAddress, busAddress, node, chipAddress, writeAddress, addrwidth, writeNumberBytes, writedata_v)


def _eeprom_data_read(server: Any, readAddress: int, readNumberBytes: int, node: int, verbose: bool = False) -> str:
    chipAddress = 0x58
    server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        
    # Data read from the EEPROM, list of hex string (single ASCII character); ['0x31', '0x31',...
    read_data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]

    # Convert each hex string to ASCII character
    read_data = list(map(hex_to_ascii, read_data))

    # Combine the list into a single string
    read_data = ''.join(read_data)

    if verbose:
        print(f'{read_data = }')
    
    return read_data


def fennec_sn_read(server: Any):
    fennec_sn_readAddress = 0x0010
    readNumberBytes = 16
    node = 0
    return _eeprom_data_read(server, fennec_sn_readAddress, readNumberBytes, node)


def imu_accel(server) -> list:
    chipAddress = 0x68
    readAddresses = [0x3B, 0x3D, 0x3F]  # [Accel_X, Accel_Y, Accel_Z]
    node = 0
    readNumberBytes = 2  # Each data point has 2 bytes

    read_data = []
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        # print(f'data1 = {_data}')
        _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
        # print(f'data2 = {hex(_data)}')
        _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
        _data = _data / 32767 * 2 * 9.8  # Convert to G force
        read_data.append(_data)
        # print(f'{read_data = }')

    # read_g_data = []
    return read_data
    

def fennec_imu_read(server: Any, verbose=False):
    chipAddress = 0x68
    readAddress = 0x75
    node = 0
    readNumberBytes = 1

    server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        
    # Data read from the EEPROM, list of hex string (single ASCII character); ['0x31', '0x31',...
    read_data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]

    # Convert each hex string to ASCII character
    # read_data = list(map(hex_to_ascii, read_data))

    # Combine the list into a single string
    read_data = ''.join(read_data)

    if verbose:
        print(f'{read_data = }')
    
    return read_data


def imu_gyro(server) -> list:
    chipAddress = 0x68
    readAddresses = [0x43, 0x45, 0x47]  # [Gyro_X, Gryo_Y, Gyro_Z]
    node = 0
    readNumberBytes = 2  # Each data point has 2 bytes

    read_data = []
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        # print(f'data1 = {_data}')
        _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
        # print(f'data2 = {hex(_data)}')
        _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
        _data = _data / 131  # Convert to angular velocity
        read_data.append(_data)
        # print(f'{read_data = }')

    # read_g_data = []
    return read_data


def imu_temp(server) -> list:
    chipAddress = 0x68
    readAddress = 0x41
    node = 0
    readNumberBytes = 2  # Each data point has 2 bytes

    server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
    _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
    # print(f'data1 = {_data}')
    _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
    # print(f'data2 = {hex(_data)}')
    _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
    # _data = _data / 131  # Convert to angular velocity
    sensitivity = 2633
    _temp_out = ((_data - 27) / sensitivity) + 25

    return _temp_out


def imu_self_test(server) -> list:
    chipAddress = 0x68
    readAddresses = [0x00, 0x01, 0x02, 0x0D, 0x0E, 0x0F]  # [XG_ST, YG_ST, ZG_ST, XA_ST, YA_ST, ZA_ST]
    node = 0
    readNumberBytes = 1  # Each data point has 2 bytes

    read_data = []
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        # print(f'data1 = {_data}')
        # _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
        # print(f'data2 = {hex(_data)}')
        # _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
        # _data = _data / 131  # Convert to angular velocity
        read_data.append(_data)
        # print(f'{read_data = }')

    return read_data


def imu_write_self_test_reg(server) -> list:
    chipAddress = 0x68
    readAddresses = [0x1B, 0x1C]  # [GYRO_CONFIG, ACCEL_CONFIG]
    node = 0
    readNumberBytes = 1  # Each data point has 2 bytes

    print('Read initial Gyro/Accel self test data...')
    read_data = []
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        # print(f'data1 = {_data}')
        # _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
        # print(f'data2 = {hex(_data)}')
        # _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
        # _data = _data / 131  # Convert to angular velocity
        # read_data.append(_data)
        print(f'{_data = }')

    print('Update Gryo/Accel register to enable self-test...')
    write_data = [0xE0, 0xE0]
    for index, writeAddress in enumerate(readAddresses):
        writedata = bytearray(write_data[index])
        writedata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, writedata)
        server.A2B_SLAVE_PERIREGISTER_WRITE(ic_name, masterAddress, busAddress, node, chipAddress, writeAddress, addrwidth, writeNumberBytes, writedata_v)

        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        print(f'{_data = }')

    print('Read updated Gyro/Accel self test data...')
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        print(f'{_data = }')

    print('Update Gryo/Accel register to disable self-test...')
    write_data = [0x00, 0x00]
    for index, writeAddress in enumerate(readAddresses):
        writedata = bytearray(write_data[index])
        writedata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, writedata)
        server.A2B_SLAVE_PERIREGISTER_WRITE(ic_name, masterAddress, busAddress, node, chipAddress, writeAddress, addrwidth, writeNumberBytes, writedata_v)

        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        print(f'{_data = }')

    print('Read updated Gyro/Accel self test data...')
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        print(f'{_data = }')


if __name__ == '__main__':
    # Initialize the SigmaStudioServer; will raise error is the APP is not loaded
    server = server_init()

    # sn = fennec_sn_read(server)

    # filename = f'{sn}.bin'
    # filename = 'mag_phase_eeprom_1121077BETA10090.bin'
    # print(f'Looking for {filename}...')
    # if os.path.isfile(filename):
    #     print(f'File exists for {sn}; extract data points and begin programming...')
    #     data = extract_data_points(filename)
    # else:
    #     print('File not exist. Exiting the program...')
    #     sys.exit()
    
    # eeprom_data_write(server, data)

    fennec_imu_read(server=server, verbose=True)

    for _ in range(100):
        # print(imu_accel(server))
        print(imu_gyro(server))
        # print(imu_temp(server))
        # print(imu_self_test(server))
        # print(imu_write_self_test_reg(server))
        sleep(0.5)
        