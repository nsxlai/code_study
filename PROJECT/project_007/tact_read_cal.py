import paramiko
import json
import requests
from time import sleep, time
import codecs


__AUTHOR__ = 'ray.lai@getcruise.com'
__VER__ = '0.0.3'


# PARAMETER
HOST = '10.5.40.14'
PORT = 80
USERNAME = 'root'
PASSWORD = 'robotcar'
FILENAME = 'tact_eeprom_data.txt'


def ssh_connect():
    print('Initiating SSH connection...')
    global ssh
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=HOST, username=USERNAME, password=PASSWORD)
    return ssh


def ssh_send_cmd(cmd):
    _, ssh_stdout, _ = ssh.exec_command(cmd)
    sleep(2)
    ssh_stdout = ssh_stdout.readlines()
    temp_buf = ''.join(ssh_stdout)
    print(temp_buf)


def post_tact_param(url):
    print('Posting the TACT persistent config parameter...')
    tact_param = {'tact_array': 'molex_tact_v2'}
    r = requests.post(url, tact_param)

    if r.status_code != 200:
        raise ValueError('Unable to set the TACT persistent param...')


def get_tact_param_status():
    print('Getting the param status...')
    # url = f'http://{HOST}:{PORT}/api/v1.0/persistent-config/params'
    url = 'http://{}:{}/api/v1.0/persistent-config/params'.format(HOST, PORT)
    r = requests.get(url)

    if r.status_code == 200 and not r.json()['params'].get('tact_array'):
        post_tact_param(url)
    else:
        print('TACT persistent config is enabled')


def init_tact_data_dict() -> dict:
    tact_data = {}
    for i in range(1, 19):
        key = f'TACT{i}'
        data_format = {'calibratedOffset': [], 'calibratedSlope': []}
        tact_data.setdefault(key, data_format)
    return tact_data


def read_tact_eeprom_log() -> list:
    with open(FILENAME, 'r') as f:
        raw_tact_eeprom_data = f.readlines()
    return raw_tact_eeprom_data


def split_tact_raw_data(raw_data: dict) -> dict:
    temp_dict = {}
    start_index = 0
    line_entries_per_tact = 8  # there are 8 lines for each TACT EEPROM data in the log
    # Organize the TACT EEPROM data entries into dictionary
    for i in range(1, 19):
        key = f'TACT{i}'
        end_index = start_index + line_entries_per_tact + 1
        temp_dict.setdefault(key, raw_data[start_index+1:end_index-4])
        start_index = end_index
    return temp_dict


def _swap_byte(raw_byte: str) -> str:
    """ 1234 -> 3412 """
    return raw_byte[2:] + raw_byte[:2]


def preprocess_data(raw_data: dict) -> dict:
    temp_dict = {}
    for key, data in raw_data.items():
        data_list = []
        for element in data:
            temp = element.strip('\n')
            temp = temp.split()[1:]  # Ignoring the address field
            temp = [_swap_byte(i) for i in temp]
            temp = ''.join(temp)  # combining into 1 string
            data_list.append(temp)
        temp_dict.setdefault(key, data_list)
    return temp_dict


def _byte_convert(b: str) -> int:
    """ convert 3-byte little Endian string hex input to decimal output """
    b = b[4:] + b[2:4] + b[:2]
    return int(b, 16)


def _hex_to_ascii(hex_str: str) -> str:
    binary_str = codecs.decode(hex_str, 'hex')  # Remove the leading '0x'
    ascii_str = str(binary_str, 'utf-8')
    return ascii_str


def _tact_sn_conversion(sn_raw: str) -> str:
    sn_raw = [sn_raw[i:i + 2] for i in range(0, len(sn_raw), 2)]  # split at every 2 characters (1 byte)
    sn_raw = list(map(_hex_to_ascii, sn_raw))
    sn_raw.reverse()  # convert from little Endian format to normal
    sn_raw = ''.join(sn_raw)
    return sn_raw


def process_data(raw_data: dict) -> dict:
    tact_data = {}
    for key, data in raw_data.items():
        tact_sn_raw = data[0][:26]  # grab the first 13 ASCII characters
        # mounting_code = data[0][24:25]  # some reason the mounting code is only half byte
        tact_sn = _tact_sn_conversion(tact_sn_raw)

        cal_data_offset = 2
        temp = data[2][cal_data_offset:cal_data_offset+6]
        ch1_slope = _byte_convert(temp)
        temp = data[2][cal_data_offset+6:cal_data_offset+12]
        ch2_slope = _byte_convert(temp)
        temp = data[2][cal_data_offset+12:cal_data_offset+18]
        ch3_slope = _byte_convert(temp)

        temp = data[2][cal_data_offset+18:cal_data_offset+24]
        ch1_offset = _byte_convert(temp)
        temp = data[2][cal_data_offset+24:]
        ch2_offset = _byte_convert(temp)
        temp = data[3][:6]
        ch3_offset = _byte_convert(temp)

        tact_data[key] = {
            "serial_number": tact_sn,
            "calibratedSlope": [ch1_slope, ch2_slope, ch3_slope],
            "calibratedOffset": [ch1_offset, ch2_offset, ch3_offset]
        }
    return tact_data

"""
0x21: X-axis Sensitivity Byte-1 (Least Signigicant Byte)
0x22: X-axis Sensitivity Byte-2 
0x23: X-axis Sensitivity Byte-3 (Most Signigicant Byte)

0x24: Y-axis Sensitivity Byte-1 (Least Signigicant Byte)
0x25: Y-axis Sensitivity Byte-2 
0x26: Y-axis Sensitivity Byte-3 (Most Signigicant Byte)

0x27: Z-axis Sensitivity Byte-1 (Least Signigicant Byte)
0x28: Z-axis Sensitivity Byte-2 
0x29: Z-axis Sensitivity Byte-3 (Most Signigicant Byte)

0x2A: X-axis Zero-G-Bias Byte-1 (Least Signigicant Byte)
0x2B: X-axis Zero-G-Bias Byte-2 
0x2C: X-axis Zero-G-Bias Byte-3 (Most Signigicant Byte)

0x2D: Y-axis Zero-G-Bias Byte-1 (Least Signigicant Byte)
0x2E: Y-axis Zero-G-Bias Byte-2 
0x2F: Y-axis Zero-G-Bias Byte-3 (Most Signigicant Byte)

0x30: Z-axis Zero-G-Bias Byte-1 (Least Signigicant Byte)
0x31: Z-axis Zero-G-Bias Byte-2 
0x32: Z-axis Zero-G-Bias Byte-3 (Most Signigicant Byte)
"""


if __name__ == '__main__':
    # ssh_connect()
    # ssh_send_cmd('ls -la')
    # get_tact_param_status()

    tact_data_raw = read_tact_eeprom_log()
    tact_data_raw = split_tact_raw_data(tact_data_raw)
    tact_data_raw = preprocess_data(tact_data_raw)
    print(tact_data_raw)
    tact_data = process_data(tact_data_raw)
    print(tact_data)
