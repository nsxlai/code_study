from genericpath import isfile
from win32com.client.dynamic import Dispatch
from win32com.client import VARIANT
import pythoncom
import os
import codecs
from typing import Any, List
from time import sleep, time
import ctypes
import pandas as pd


__AUTHOR__ = 'ray.lai@getcruise.com'
__version__ = '1.6.0'

# SigmaStudio Files
SigmaStudioServer = 'Analog.SigmaStudioServer.SigmaStudioServer'
project_file_path = 'C:\\Users\\hardware R&D\\Documents\\Fennec_EV_Test_v5 (IMU)'
project_file_name = 'FENNEC_A2B_1Node_24bit_R1_EV_IMU.dspproj'
project_file = os.path.join(project_file_path, project_file_name)


# Hardware constants
ic_name = VARIANT( pythoncom.VT_BYREF | pythoncom.VT_BSTR, "IC 1")
masterAddress = 0x68
busAddress = 0x69
addrwidth = 1
writeNumberBytes = 4
readdata = bytearray(8)
readdata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, readdata)


def server_init(verbose: bool = False) -> Any:
    """ This function will link1/compile/download the DSP project file code to Fennec. If the project code is not
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


def time_elapse(func):
    def wrapper_func(*args, **kwargs):
        start_time = time()
        func(*args, **kwargs)
        end_time = time()
        print(f'Time elapsed: {end_time-start_time}')
        return
    return wrapper_func


def _imu_write_reg_value(server: Any, writeAddress: int, writeData: int) -> None:
    """
    Write the IMU register value 1 byte at a time
    """
    chipAddress = 0x68
    node = 0
    writeNumberBytes = 1
    
    writeData = str(hex(writeData))  # writeData should be in str format
    writedata = bytearray(codecs.decode(writeData[2:].zfill(2), 'hex'))  # Also remove the '0x' from the hex data header; zfill is for in case of '0' (need '00' instead)
    writedata_v = VARIANT( pythoncom.VT_ARRAY | pythoncom.VT_BYREF | pythoncom.VT_UI1, writedata)

    server.A2B_SLAVE_PERIREGISTER_WRITE(ic_name, masterAddress, busAddress, node, chipAddress, writeAddress, addrwidth, writeNumberBytes, writedata_v)


def imu_temp(server) -> list:
    chipAddress = 0x68
    readAddress = 0x41
    node = 0
    readNumberBytes = 2  # Each data point has 2 bytes

    server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
    _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
    _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
    _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
    sensitivity = 326.8
    roomTemp_offset = 2400
    _temp_out = ((_data - roomTemp_offset) / sensitivity) + 25
    return _temp_out


def imu_self_test_code(server, verbose: bool = False) -> list:
    """
    Read the GYRO and ACCEL self test code (ST_CODE). The output value does not convert to signed value like the GYRO and ACCEL output
    """
    chipAddress = 0x68
    readAddresses = [0x00, 0x01, 0x02, 0x0D, 0x0E, 0x0F]  # [XG_ST, YG_ST, ZG_ST, XA_ST, YA_ST, ZA_ST]
    node = 0
    readNumberBytes = 1  # Each data point has 2 bytes

    read_st_data = []
    for readAddress in readAddresses:
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, readAddress, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        _data = _data[0]
        read_st_data.append(_data)

    if verbose:
        print(f'{read_st_data = }')
    gyro_st_data = [int(hex_val, 16) for hex_val in read_st_data[:3]]
    accel_st_data = [int(hex_val, 16) for hex_val in read_st_data[3:]]
    return gyro_st_data, accel_st_data


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


def _imu_read_reg_value(server, reg_val: int) -> list:
    """
    - Supporting function to imu_gyro_accel_output. This function will read the values from the provided reg_val parameter.
    - Will read 2 bytes by default from the reg_val (e.g., if reg_val = 0x40, this function will read both 0x40 and 0x41)
    - Due to the nature of IMU data being very sensitive (both gyro and accel), this function will read number_of_samples and store the values in a list.
    - The recommended value from TDK is 200 samples; however, 50 samples can achieve similar result (pass) with much faster run time
    """
    chipAddress = 0x68
    node = 0
    readNumberBytes = 2  # Each data point has 2 bytes
    number_of_samples = 50

    read_data = []
    for i in range(number_of_samples):
        server.A2B_SLAVE_PERIREGISTER_READ(ic_name, masterAddress, busAddress, node, chipAddress, reg_val, addrwidth, readNumberBytes, readdata_v)
        _data = [hex(readdata_v.value[byte]) for byte in range(readNumberBytes)]
        _data = int(_data[0], 16) << 8 | int(_data[1], 16)  # Shift high byte 8 bits and add the low bytes with OR operator
        _data = ctypes.c_int16(_data).value  # Convert unsigned_int16 to signed_int16
        read_data.append(_data)
    return read_data


def imu_gyro_accel_output(server, verbose: bool = False) -> list:
    """
    This function will gather the GYRO or ACCEL output from IMU20680 chipset
    """
    GYRO_X_OUT = 0x43  # GYRO_X_OUT is actually 2 bytes, the imu_read_value will automatically read 2 byte from the provided register address
    GYRO_Y_OUT = 0x45  # The _imu_read_reg_value will automatically read 2 bytes
    GYRO_Z_OUT = 0x47
    ACCEL_X_OUT = 0x3B
    ACCEL_Y_OUT = 0x3D
    ACCEL_Z_OUT = 0x3F

    GYRO_OUT = [GYRO_X_OUT, GYRO_Y_OUT, GYRO_Z_OUT]
    ACCEL_OUT = [ACCEL_X_OUT, ACCEL_Y_OUT, ACCEL_Z_OUT]

    # Read GYRO output data
    gyro_output = []
    for reg in GYRO_OUT:
        gyro_value_list = _imu_read_reg_value(server, reg)
        _avg = sum(gyro_value_list) / len(gyro_value_list)
        gyro_output.append(_avg)
    
    # Read ACCEL output data
    accel_output = []
    for reg in ACCEL_OUT:
        accel_value_list = _imu_read_reg_value(server, reg)
        _avg = sum(accel_value_list) / len(accel_value_list)
        accel_output.append(_avg)
    
    if verbose:
        print(f'{gyro_output = }')
        print(f'{accel_output = }')

    return gyro_output, accel_output


def st_otp_calc(ST_code, FS_sel):
    """
    Calculate the ST_OTP value from the ST_CODF with the provided formula
    """
    ST_OTP = (2620/2**FS_sel) * (1.01**(ST_code - 1))
    return ST_OTP


if __name__ == '__main__':
    """
    Use the "AN-000143 IAM-20680xx Accel and Gyro Self-Test Implementation_v2.0.pdf" Datasheet for the self test reference below.

    There are 2 ways of getting GYRO and ACCEL data from the IMU
    1. Enable FIFO and read from FIFO directly. The datasheet suggests 200 samples (GYRO + ACCEL).
    2. Read the GYRO and ACCEL output register directly. The datasheet suggestion 200 samples (GYRO + ACCEL).

    If read from the FIFO directly, need to read the FIFO buffer (0x74) without ACK so the read can be done in quickly succession.
    If read the values from the GYRO and ACCEL registers directly, the ACK will be applied automatically. This code will poll
    only 50 samples (GYRO + ACCEL) instead of 200 to save time. The precision between differen sample size is roughly the same.
    """
    # Initialize the SigmaStudioServer; will raise error is the APP is not loaded; default selftest will be disabled when power up
    server = server_init(verbose=True)

    imu_temperature = imu_temp(server)
    print(f'imu_temperature = {imu_temperature:6.2f}C')

    # Create the Pandas DataFrame to store the selftest data    
    df_selftest = pd.DataFrame(data=None, index=['Gx', 'Gy', 'Gz', 'Ax', 'Ay', 'Az'], columns=['ST_meas_on', 'ST_meas_off'])

    # Read GYRO and ACCEL data; self test is disabled (off)
    print('Read GYRO and ACCEL data; self test is disabled')
    gyro_st_off, accel_st_off = imu_gyro_accel_output(server)
    
    # Enable GYRO self test (reg=0x1B, value=0xE0)
    _imu_write_reg_value(server, writeAddress=0x1B, writeData=0xE0)

    # Enable ACCEL self test (reg=0x1C, value=0xE0)
    _imu_write_reg_value(server, writeAddress=0x1C, writeData=0xE0)

    # Read GYRO and ACCEL data; self test enabled (on)
    print('Read GYRO and ACCEL data; self test is enabled')
    gyro_st_on, accel_st_on = imu_gyro_accel_output(server)

    # Populate the read values to the df_selftest
    df_selftest['ST_meas_off'] = gyro_st_off + accel_st_off
    df_selftest['ST_meas_on'] = gyro_st_on + accel_st_on
    df_selftest['ST_diff'] = df_selftest['ST_meas_on'] - df_selftest['ST_meas_off']

    # Fetch the 1 byte GYRO and ACCEL ST_CODE from the IMU chipset
    gyro_st_code, accel_st_code = imu_self_test_code(server)
    df_selftest['ST_DATA'] = gyro_st_code + accel_st_code

    # Calculate factory self tests values (xx_ST_FV)
    GYRO_FS_SEL = 0b00
    ACCEL_FS_SEL = 0b00 
    gyro_st_otp = [st_otp_calc(ST_code, GYRO_FS_SEL) for ST_code in gyro_st_code]
    accel_st_otp = [st_otp_calc(ST_code, ACCEL_FS_SEL) for ST_code in accel_st_code]
    df_selftest['ST_OTP'] = gyro_st_otp + accel_st_otp

    # Final pass/fail calculation
    df_selftest['ST_ratio'] = df_selftest['ST_diff'] / df_selftest['ST_OTP']
    df_selftest['ST_pass'] = (df_selftest['ST_ratio'] < 1.5) & (df_selftest['ST_ratio'] > 0.5)

    # Display final result
    print('-' * 77)
    pd.set_option('display.precision', 3)  # Set 3 digits to the left of the decimal point
    print(df_selftest)

    """
        ST_meas_on  ST_meas_off   ST_diff  ST_DATA     ST_OTP  ST_ratio  ST_pass
    Gx    17108.52        75.94  17032.58      189  17010.597     1.001     True
    Gy    17371.30      -120.94  17492.24      191  17352.510     1.008     True
    Gz    19033.08        56.50  18976.58      200  18978.185     1.000     True
    Ax     7363.76      -398.16   7761.92      111   7828.029     0.992     True
    Ay     6725.20      -151.12   6876.32       98   6878.196     1.000     True
    Az    -9119.52    -16284.72   7165.20      107   7522.582     0.952     True

    For Gyro, the ST_ratio > 0.5 is PASS
    For ACCEL, the 0.5 < ST_ratio < 1.5 is PASS 
    """

    # Disable GYRO self test (reg=0x1B, value=0xE0)
    _imu_write_reg_value(server, writeAddress=0x1B, writeData=0x00)

    # Disable ACCEL self test (reg=0x1C, value=0xE0)
    _imu_write_reg_value(server, writeAddress=0x1C, writeData=0x00)
