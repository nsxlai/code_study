import codecs


def int_func_case_1():
    """
    Use a random number and convert the number from various bases to decimal

    The int() function returns an integer object constructed from a number or string x,
    or return 0 if no arguments are given.
    """
    val = 64  # decimal 64
    val = str(val)
    print(f'{val = }; {type(val) = }')
    # int function can display a number in different bases; however, the input value has to change to string first
    # e.g., int(val, base=16) treats val as a base 12 number
    # the output of the int function translate to base 10 number
    print(f'{int(val, base=8) = }')
    print(f'{int(val, base=10) = }')
    print(f'{int(val, base=12) = }')
    print(f'{int(val, base=16) = }')

    try:
        print(f'{int(val, base=4) = }')
    except ValueError as e:
        print('Try to print int(val, base=4) but encounter ValueError')
        print('Val = 64; "6" does not exist in base 4 numbering')
        print(e)


def int_func_case_2():
    val = '100'
    print(f'{int(val, base=2) = }')
    print(f'{int(val, base=4) = }')
    print(f'{int(val, base=8) = }')
    print(f'{int(val, base=16) = }')

    try:
        print(f'{int(val, base=64) = }')
    except ValueError as e:
        print('Try to print int(val, base=64) but encounter ValueError')
        print(e)


if __name__ == '__main__':

    # 1. Change from any number with different base to decimal (base=10)
    print('Example 1')
    int_func_case_1()
    print('-' * 40)
    int_func_case_2()
    print('-' * 40)

    # 2. Convert to and from binary
    print('Example 2')
    val = 79
    # Base 2(binary)
    bin_a = bin(val)
    print(bin_a)
    print(int(bin_a, 2))  # Base 2(binary)

    # 3. Convert to and from octal
    print('-' * 40)
    print('Example 3')
    val = 70
    oct_a = oct(val)
    print(oct_a)
    print(int(oct_a, 8))

    # 4. Convert to and from hexdecimal
    print('-' * 40)
    print('Example 4')
    val = 256
    hex_a = hex(val)
    print(hex_a)
    print(int(hex_a, 16))

    # 5. Convert hex to ASCII
    print('-' * 40)
    print('Example 5')
    hex_string = "0x42455441"[2:]  # Remove 0x header
    bytes_object = bytes.fromhex(hex_string)
    ascii_string = bytes_object.decode("ASCII")
    print(f'hex_string {hex_string} = ascii_string {ascii_string}')

    # 6. Convert hex to ASCII, different solution
    print('-' * 40)
    print('Example 6')
    hex_str = '0x3131323130343542455441'[2:]
    binary_str = codecs.decode(hex_str, 'hex')
    ascii_str = str(binary_str, 'utf-8')
    print(f'{ascii_str = }')

    # 7. Use F-string
    print('-' * 40)
    a = 0x0010
    print(f'{a = }')
    print(f'a:x = {a:x}')
    print(f'a:o = {a:o}')
    print(f'a:b = {a:b}')
