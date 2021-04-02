#!/usr/bin/python3
import requests
import argparse


IP_ADDR = '10.1.1.2'
PORT = '80'
API_VER = 'v1.0'
API_HEADER = f'http://{IP_ADDR}:{PORT}/api/{API_VER}'
bank_0_ports = [0, 1, 2, 3]
bank_1_ports = [4, 5, 6, 7]

# Create the parser
my_parser = argparse.ArgumentParser(description='SPAM Test Utility')

# Add the arguments
my_parser.add_argument('-s', '--solenoid', type=str, help='Turn solenoid bank on or off. E.g., "-s on", "--solenoid off"')
my_parser.add_argument('-b', '--solenoid_bank', type=int, help='Select solenoid bank 0 or 1')
my_parser.add_argument('-f', '--fan', type=str, help='Turn fan on or off. E.g., "-f on", "--fan off"' )
my_parser.add_argument('-v', '--sw_version', help='Display SW version')
my_parser.add_argument('-i', '--hwinfo', help='Display HW information')

# Execute the parse_args() method
args = my_parser.parse_args()


def solenoid_on(chan: int, verbose: bool = False) -> None:
    r = requests.post(f'{API_HEADER}/spam/solenoid_on/{chan}')
    if verbose:
        print(r.json())


def solenoid_off(chan: int, verbose: bool = False) -> None:
    r = requests.post(f'{API_HEADER}/spam/solenoid_off/{chan}')
    if verbose:
        print(r.json())


if __name__ == '__main__':
    print(args.solenoid)
    print(args.solenoid_bank)

    if args.solenoid.lower() == 'on' and args.solenoid_bank == 0:
        for port in bank_0_ports:
            solenoid_on(port)

    elif args.solenoid.lower() == 'on' and args.solenoid_bank == 1:
        for port in bank_1_ports:
            solenoid_on(port)

    elif args.solenoid.lower() == 'off' and args.solenoid_bank == 0:
        for port in bank_0_ports:
            solenoid_off(port)

    elif args.solenoid.lower() == 'off' and args.solenoid_bank == 1:
        for port in bank_1_ports:
            solenoid_off(port)

    resp = requests.get('http://10.1.1.2:80/api/v1.0/trace/hwinfo')
    # if resp.status_code != 201:
    #     # This means something went wrong.
    #     raise ApiError('GET /tasks/ {}'.format(resp.status_code))

    print(resp.json())

    resp = requests.get('http://10.1.1.2:80/api/v1.0/swupdate/sw-versions/rootfs')
    print(resp.json())

    resp = requests.get('http://10.1.1.2:80/api/v1.0/spam/cpu_check/lscpu')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/fan_speed/set/100')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/fan_on')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/fan_off')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_on/0')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_on/1')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_on/2')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_on/3')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_off/0')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_off/1')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_off/2')
    print(resp.json())

    resp = requests.post('http://10.1.1.2:80/api/v1.0/spam/solenoid_off/3')
    print(resp.json())
