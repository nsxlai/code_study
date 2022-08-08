import subprocess


def extract_data_points(filename: str) -> Dict:
    data = []
    windows_os_slice = slice(8, 57)
    linux_slice = slice(10, 57)

    p = subprocess.Popen(f'hexdump -C {filename}', shell=True, stdout=subprocess.PIPE)
    for line in p.stdout:
        temp = line.decode(encoding='utf-8', errors='ignore')  # encode with utf-8
        temp = temp[linux_slice].replace(' ', '')  # remove the space between each byte, for 4 bytes (1 line)

        for i in range(len(temp)):  # each line has 4 bytes, break down the 4 bytes and appends to data list
            over_arr_len = (i + 8) > (len(temp) - 1)
            if i % 8 == 0 and not over_arr_len:
                data.append(temp[i:i + 8])
            elif over_arr_len:
                data.append(temp[i:])
                break  # break out of the loop after the last element is added
    return data
