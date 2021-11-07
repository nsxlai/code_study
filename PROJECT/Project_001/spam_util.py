#!/usr/bin/env python
import requests
import argparse
import os
import paramiko
from typing import Optional
from pprint import pprint
from config import spam_dut, IP_ADDR
from time import sleep
from tqdm import tqdm
from threading import Thread

__VERSION__ = '3.5'
__AUTHUR__ = 'ray.lai@getcruise.com'

# Create the parser
my_parser = argparse.ArgumentParser(description='SPAM Test Utility')

# Add the arguments
my_parser.add_argument('-s', '--solenoid', type=str,
                       help='Turn solenoid bank on or off. E.g., "-s on", "--solenoid off"')
my_parser.add_argument('-b', '--solenoid_bank', type=int, help='Select solenoid bank 0 or 1')
my_parser.add_argument('-f', '--fan', type=str, help='Turn fan on or off. E.g., "-f on", "--fan off"')
my_parser.add_argument('-v', '--swinfo', help='Display SW version', action='store_true')  # Don't need argument after -v
my_parser.add_argument('-i', '--hwinfo', help='Display HW information',
                       action='store_true')  # Don't need argument after -i
my_parser.add_argument('-c', '--cpuinfo', help='Display CPU information',
                       action='store_true')  # Don't need argument after -c
my_parser.add_argument('-n', '--network_traffic_runtime', type=int,
                       help='Run IPERF3 traffic at full BW. E.g., -n 10 = run IPERF traffic for 10 sec in each direction (20 sec total)')
my_parser.add_argument('-t', '--temperature_humidity',
                       help='Read temperature and humidity sensor', action='store_true')
my_parser.add_argument('-g', '--stress_test', type=int,
                       help='Run Stress NG test on CPU and DDR memory. E.g., -g 10 = run Stress NG test for 10 seconds')
my_parser.add_argument('-m', '--initial_setup', action='store_true',
                       help='When SPAM DUT or the RPi is rebooted, this option will setup the network and trusted boundry between the 2 devices')
my_parser.add_argument('--verbose', help='Verbose for debug purpose', action='store_true')

# Execute the parse_args() method
args = my_parser.parse_args()


class SolenoidError(Exception):
    pass


class FanError(Exception):
    pass


def info(info_type: dict):
    """ Use polymorphism to share common info display function
        This function uses only API GET to fetch the data
    """
    r = requests.get(info_type.get('api'))
    print(f"\n{info_type.get('desc')}")
    pprint(r.json())


def feature(feature_type: dict, port: Optional[int], verbose: bool = args.verbose) -> bool:
    """
    Use polymorphism to share common set function
    This function uses only API POST to send the data
    :param feature_type: e.g., enable solenoid (-s) or fan (-f)
    :param port: e.g., solenoid 0 - 7
    :param verbose: To enable verbose messaging during the API execution; debugging purpose
    :return: True for failure occurred or False for no failure
    """
    fail_flag = False
    if port is None:
        print(f"{feature_type.get('desc')}")
        r = requests.post(f"{feature_type.get('api')}")
    else:
        print(f"{feature_type.get('desc')} {port}")
        r = requests.post(f"{feature_type.get('api')}/{port}")

    if r.json().get('status') != 'success':
        fail_flag = True
    if verbose:
        pprint(r.json())
    return fail_flag


def solenoid(s_state: str, s_bank: int) -> None:
    fail_flag = False
    if s_state.lower() == 'on' and s_bank == 0:
        for port in spam_dut.get('bank_0_ports'):
            fail_flag = feature(spam_dut.get('solenoid_on'), port)

    elif s_state.lower() == 'on' and s_bank == 1:
        for port in spam_dut.get('bank_1_ports'):
            fail_flag = feature(spam_dut.get('solenoid_on'), port)

    elif s_state.lower() == 'off' and s_bank == 0:
        for port in spam_dut.get('bank_0_ports'):
            fail_flag = feature(spam_dut.get('solenoid_off'), port)

    elif s_state.lower() == 'off' and s_bank == 1:
        for port in spam_dut.get('bank_1_ports'):
            fail_flag = feature(spam_dut.get('solenoid_off'), port)

    else:
        print('Invalid solenoid command!!')

    if fail_flag:
        raise SolenoidError('Unable to turn on/off at least one of the solenoid ports')
    return


def fan(f_state: str) -> None:
    fail_flag = False
    if f_state.lower() == 'on':
        fail_flag = feature(spam_dut.get('fan_speed_set'), port=100)  # Set fan speed = 100%
        fail_flag = feature(spam_dut.get('fan_on'), port=None)

    elif f_state.lower() == 'off':
        fail_flag = feature(spam_dut.get('fan_off'), port=None)

    else:
        print('Invalid fan command!!')

    if fail_flag:
        raise FanError('Unable to turn on/off fan ports')
    return


def iperf_traffic_server_setup_method_1() -> None:
    """
    This method pipes the SSH request and the DUT execute commands together. To get around the password, the script
    side PC can create the SSH key pair and copy the public key to the DUT to avoid password authentication. This
    is more customized and more suitable for lab environment (not MFG environment).
    """
    print('Start up IPERF server on SPAM DUT')
    os.system(f"ssh {spam_dut.get('username')}@{IP_ADDR} {spam_dut.get('iperf_svr').get('cmd')} -p "
              f"{spam_dut.get('traffic').get('send').get('port')}")
    os.system(f"ssh {spam_dut.get('username')}@{IP_ADDR} {spam_dut.get('iperf_svr').get('cmd')} -p "
              f"{spam_dut.get('traffic').get('recv').get('port')}")
    return


def iperf_traffic_server_setup_method_2() -> None:
    """
    This method uses Python Paramiko library to handle the SSH command and password management. More ideal if the DUT
    get swapped often
    """
    print('Start up IPERF server on SPAM DUT')
    server_send_cmd = f"{spam_dut.get('iperf_svr').get('cmd')} -p {spam_dut.get('traffic').get('send_port')}"
    server_recv_cmd = f"{spam_dut.get('iperf_svr').get('cmd')} -p {spam_dut.get('traffic').get('recv_port')}"

    ssh = paramiko.SSHClient()
    ssh.connect(IP_ADDR, username=spam_dut.get('username'), password=spam_dut.get('password'))

    for cmd in [server_send_cmd, server_recv_cmd]:
        _, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        print(ssh_stdout)
        if ssh_stderr:
            raise ChildProcessError('Error has occurred during the SSH session at the DUT side!')


def _iperf_traffic_client_run(traffic_direction: str, runtime: int, verbose: bool = args.verbose) -> None:
    dir_flag = ''
    dir_flag = '-R' if traffic_direction == 'recv' else dir_flag

    test_cmd = f"iperf3 -c {IP_ADDR} -p {spam_dut.get('traffic').get(traffic_direction).get('port')} " \
               f"-t {runtime} -O 15 -i 15 {dir_flag} >> " \
               f"{spam_dut.get('traffic').get(traffic_direction).get('log')}"
    if verbose:
        print(test_cmd)
    os.system(test_cmd)


def _progress_bar(runtime: int) -> None:
    for _ in tqdm(range(runtime)):
        sleep(1)


def _iperf_traffic_thread_split(traffic_direction: str, runtime: int) -> None:
    thread1 = Thread(target=_iperf_traffic_client_run, args=(traffic_direction, runtime,))
    thread2 = Thread(target=_progress_bar,
                     args=(runtime + 15,))  # account for 15 second omitted in the beginning of IPERF
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def iperf_traffic(runtime: int = args.network_traffic_runtime) -> None:
    print('Running IPERF traffic...')
    send_log = spam_dut.get('traffic').get('send').get('log')
    recv_log = spam_dut.get('traffic').get('recv').get('log')
    os.system(f"date > {send_log}")
    os.system(f"date > {recv_log}")

    half_runtime = runtime // 2  # Run half of the run time per each direction; half_runtime: int
    print(f'Running forward traffic for {half_runtime} seconds')
    _iperf_traffic_thread_split('send', half_runtime)

    print(f'\nRunning reverse traffic for {half_runtime} seconds')
    _iperf_traffic_thread_split('recv', half_runtime)
    return


def iperf_traffic_analysis(traffic_direction: str) -> None:
    """
    Polymorphism for dictionary entry fetch. The dictionary key is 'traffic'. The function will fetch the 'log' key for the
    difference send or recv filename.
    """
    log = spam_dut.get('traffic').get(traffic_direction).get('log')
    data = os.popen(f"tail -n 5 {log}").read().split('\n')
    data = data[1].split()
    BW, unit, retr = data[6], data[7], data[8]
    print('-' * 30)
    print(f'Average BW: {BW} {unit}')
    print(f'Dropped packet (retr): {retr}')

    # Check 1: BW
    limit_dict = spam_dut.get('traffic').get(
        unit.lower())  # use either gbit/sec or mbit/sec to fetch the upper/lower limit
    if limit_dict.get('lower_limit') < int(BW) < limit_dict.get('upper_limit'):
        print(f'{traffic_direction} BW check PASSED!')
    else:
        print(f'{traffic_direction} BW check FAILED!')

    # Check 2: Retransmission
    if int(retr) <= spam_dut.get('traffic').get('retr_limit'):
        print(f'{traffic_direction} RETR check PASSED!')
    else:
        print(f'{traffic_direction} RETR check FAILED!')
    return


def _sensor_data_conversion(raw_data: list) -> int:
    combine_str = raw_data[0] + raw_data[1][2:]  # e.g., merge '0x6d' and '0x42' into '0x6d42'
    return int(combine_str, 16)  # translate base 16 string into base 10 integer


def _display_temp(temp: int) -> None:
    temp_val = (temp / 65535) * 175 - 45
    print(f'Temperature = {temp_val:7.3f}C')


def _display_hum(hum: int) -> None:
    hum_val = (hum / 65535) * 100
    print(f'Humidity = {hum_val:7.3f}%')


def read_sensor() -> None:
    """
    raw_data output will be in 6 bytes of string in a list; containing both temperature and humidity
    Temperature data will be the first 2 bytes, the third byte is the temperature data CRC
    Humidity data will be the 4th and 5th bytes, the 6th byte is the humidity data CRC

    for example: raw_data will be ['0x6d', '0x42', '0x33', '0x45', '0x6a', '0xaa']
    Temperature = ['0x6d', '0x42']
    Humidity = ['0x45', '0x6a']
    """
    raw_data = os.popen(f"ssh {spam_dut.get('username')}@{IP_ADDR} {spam_dut.get('temp').get('cmd')}").read().split()
    temp_int = _sensor_data_conversion(raw_data[:2])  # Temperature; 2 bytes
    hum_int = _sensor_data_conversion((raw_data[3:5]))  # Humidity; 2 bytes
    _display_temp(temp_int)
    _display_hum(hum_int)


def _stress_test_run(runtime: int, verbose: bool = args.verbose) -> None:
    stress = spam_dut.get('stress')
    test_cmd = f"ssh {spam_dut.get('username')}@{IP_ADDR} {stress.get('cmd')} {runtime} 2>> {stress.get('log')}"
    if verbose:
        print(test_cmd)
    os.system(f"date > {stress.get('log')}")
    os.system(test_cmd)  # capture stderr


def _stress_test_thread_split(runtime: int) -> None:
    thread1 = Thread(target=_stress_test_run, args=(runtime,))
    thread2 = Thread(target=_progress_bar, args=(runtime,))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


def stress_test(runtime: int) -> None:
    print('Running Stress NG CPU and DRAM test...')
    _stress_test_thread_split(runtime)

    print('-' * 30)
    stress = spam_dut.get('stress')
    raw_capture = os.popen(f"tail -n 1 {stress.get('log')}").read()
    if 'successful' in raw_capture:
        print('Stress Test PASSED!')
    else:
        print('Stress Test FAILED!')


def initial_setup() -> None:
    """
    The Initial setup will include the following:
    1. Setup the RPi Eth0 IP address to 10.1.1.1
    2. Add SPAM DUT IP address (10.1.1.2) to the RPi routing table
    """
    rpi = spam_dut.get('rpi')
    print('Setup RPI Eth0 IP address...')
    os.system(rpi.get('ip_addr').get('set_cmd'))
    sleep(5)
    print(os.system(rpi.get('ip_addr').get('chk_cmd')))

    print('Add SPAM DUT IP address to the RPi routing table...')
    os.system(rpi.get('routing_table').get('set_cmd'))
    print(os.system(rpi.get('routing_table').get('chk_cmd')))

    # print('Transfer the RPi public key to SPAM DUT...')
    # os.system('ssh-copy-id -i ~/.ssh/id_rsa root@10.1.1.2')


if __name__ == '__main__':
    print(f'utility version {__VERSION__}')

    if args.verbose:
        print(f'Verbose mode: {args.verbose}')

    if args.hwinfo:
        info(spam_dut.get('hwinfo'))

    if args.swinfo:
        info(spam_dut.get('swinfo'))

    if args.cpuinfo:
        info(spam_dut.get('cpuinfo'))

    if all([args.solenoid, args.solenoid_bank in [0, 1]]):
        solenoid(args.solenoid, args.solenoid_bank)

    if args.fan:
        fan(args.fan)

    if args.network_traffic_runtime:
        iperf_traffic_server_setup_method_1()
        iperf_traffic()
        iperf_traffic_analysis('send')
        iperf_traffic_analysis('recv')

    if args.temperature_humidity:
        read_sensor()

    if args.stress_test:
        stress_test(args.stress_test)

    if args.initial_setup:
        initial_setup()
