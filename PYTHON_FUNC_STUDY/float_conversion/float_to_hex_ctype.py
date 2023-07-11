"""
source: https://stackoverflow.com/questions/16444726/binary-representation-of-float-in-python-bits-not-hex
"""
import ctypes


if __name__ == '__main__':
    f = 971.220057
    s = 0x4472CE15

    print(f'Original value = {f}')
    bin_val = bin(ctypes.c_uint32.from_buffer(ctypes.c_float(f)).value)
    print(f'{bin_val = }, {type(bin_val) = }')

    hex_val = hex(int(bin_val, 2))
    print(f'{hex_val = }')

    original_val = ctypes.c_float.from_buffer(ctypes.c_uint32(int(bin_val, 2))).value
    print(f'original_val = {original_val:.10}')
