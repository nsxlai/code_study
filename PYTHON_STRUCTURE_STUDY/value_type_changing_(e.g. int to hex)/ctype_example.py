"""
source: https://stackoverflow.com/questions/1375897/how-to-get-the-signed-integer-value-of-a-long-in-python
source: https://www.tutorialspoint.com/two-s-complement
"""
import ctypes


if __name__ == '__main__':
    """
    In the example here, convert 2-byte integer (2**16 = 65535) range from
        unsigned: 0 - 65535 to
        signed:  -32768 - 32767
    """
    val = 54345  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 0  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 23456  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 32767  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 32768  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 32769  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')

    val = 65535  # Convert this unsigned integer to signed integer
    new_val = ctypes.c_int16(val).value
    print(f'{val = }, {new_val = }')
