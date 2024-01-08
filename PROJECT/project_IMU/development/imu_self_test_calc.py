from math import log10


if __name__ == '__main__':
    
    # st_fac = 0x1CB4  # self test accelerometer X value
    st_fac = 0x1A14  # self test accelerometer Y value
    FS = 2  # -2g to +2g
    ST_OTP = 0x6F

    c_val = 2620 / (2**FS)
    print(f'{c_val = }')

    n = log10(st_fac/c_val)
    print(f'{st_fac = }')
    print(f'{n = }')

    st_code = round(n / log10(1.01)) + 1
    print(f'{st_code = }')

    t_val = c_val * (1.01**(st_code-1))
    print(f'{t_val = }')

    t_val = int(t_val)
    print(f'{t_val = }')
    print(f't_val = {t_val:x}')

    print(f'ST_OTP = {ST_OTP:x}')

    