'''
source: https://stackoverflow.com/questions/14504323/how-can-i-convert-32-bit-binary-number-to-floating-point-number
        https://stackoverflow.com/questions/1425493/convert-hex-to-binary

Single precision:
For your number (00111111010000000000000000000000)

Sign: 0 is +
Exponent: 01111110 is -1 (126-127)
Significand: 10000000000000000000000 is 1.5 (The 'invisible' first bit gives you 1, then the second bit (only one set) is 0.5, the next one would have been 0.25, then 0.125 and so on)


You then calculate the value as such:

sign * 2^exp * Significand

1 * 2^-1 * 1.5
1 * 0.5 * 1.5
0.75
'''


def bin_str_to_float_conv(bin_str: str) -> float:
    sign = 1 if bin_str[0] == '0' else -1  # 0 = positive and 1 = negative
    exponent = bin_str[1:9]
    significand = bin_str[9:]
    print(f'{sign = }')
    print(f'{exponent = }')
    print(f'{significand = }')

    num_exponent = int(exponent, 2) - 127
    cur_multiplier = pow(2, num_exponent)
    print(f'{num_exponent = }')
    print(f'{cur_multiplier = }')

    cur_float = 1.0
    for idx, val in enumerate(significand):
        if val == '1':
            temp_float = 1 / pow(2, idx+1)
            print(f'{temp_float = }')
            cur_float += temp_float
            print(f'{cur_float = }')

    return sign * cur_multiplier * cur_float


if __name__ == '__main__':
    # float_num_hex = 0x000001DA
    # float_num_hex = 0xfffffcfe
    float_num_hex = 0xfffffff0
    float_num_hex = 0x00001fae
    float_num_binary_str = bin(float_num_hex)[2:].zfill(32)  # [2:] will remove the '0b' header and zfill will add 0s
    print(f'{float_num_binary_str =}')

    final = bin_str_to_float_conv(float_num_binary_str)
    print(f'{final = }')
