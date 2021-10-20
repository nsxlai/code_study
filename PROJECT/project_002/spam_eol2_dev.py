#!/usr/bin/python
import paramiko
import sys
import os
from pathlib import Path

HOST = '10.1.1.2'
USERNAME = 'root'
PASSWORD = 'robotcar'

hw_info = {'cpu': {'BogoMIPS': '66.66',
                   'Features': 'fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid',
                   'CPU_implementer': '0x41',
                   'CPU_architecture': '8',
                   'CPU_variant': '0x0',
                   'CPU_part': '0xd03',
                   'CPU_revision': '4'},
           'cpu_freq': '1199999',
           'os_release': 'VERSION=2020.02.1-g52bd7ffe7d',
           'kernel': '5.4.0',
           'sw_version': {'rootfs': '2.1.0-f744055d9475730647b0a9a3a2307296bb8ce880',
                          'buildroot': '52bd7ffe7d0f28c6a6567191a181f8bed2489909',
                          'linux': 'xilinx-v2020.2-cruise.9',
                          'uboot': 'xilinx-v2020.2-cruise.2',
                          'vivado_fw': '1.0.0-0ad02ff67f9d9d0b116d17a81bf7e0514e5f9e94',
                          'build_type': 'eng'},
           'emmc': {'fw_rev': '0x3339313032343137',
                    'hw_rev': '0x0'},
           }


def ssh_connect():
    print('Initiating SSH connection...')
    global ssh_client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOST, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)
    # with username/password set, no need to "look_for_keys" file


def check_cpu(verbose=False):
    """ If passing all tests, the function will return nothing; however, if any test fails, will exit  """
    print('\nChecking CPU info')
    seq = ['BogoMIPS', 'Features', 'CPU_implementer', 'CPU_architecture', 'CPU_variant',
           'CPU_part', 'CPU_revision']
    stdin, stdout, _ = ssh_client.exec_command('cat /proc/cpuinfo')
    temp_buf = stdout.readlines()
    # pprint(temp_buf)
    start_ptr = 1  # start the check at the first line (not zeroth)
    for cpu_num in range(4):
        for check in seq:
            if verbose:
                print(f'hw_info check = {hw_info.get("cpu").get(check)}')
                print(f'temp_buf = {temp_buf[start_ptr]}')
            print(f'CPU num {cpu_num} check: {check}'.ljust(40, '.'), end='')
            if hw_info.get('cpu').get(check) in temp_buf[start_ptr]:
                print('PASSED')
            else:
                print('FAILED')
                sys.exit()
            temp_buf.pop(start_ptr)
        temp_buf.pop(start_ptr)  # Popping the extra blank space between each processor block
        start_ptr += 1

    if verbose:
        print(f'\nCPU entry = {temp_buf}')
    print('Check number of processors: '.ljust(40, '.'), end='')
    if len(temp_buf) == 4:
        print('PASSED')
    else:
        print('FAILED')
        sys.exit()
    return


def check_cpu_freq(verbose=False):
    """ Check CPU frequencies on all CPU cores """
    print('\nCPU Core Frequency Check')
    for core in range(4):
        cmd = f'cat /sys/bus/cpu/devices/cpu{core}/cpufreq/cpuinfo_cur_freq'
        stdin, stdout, _ = ssh_client.exec_command(cmd)
        temp_buf = stdout.readlines()
        if verbose:
            print(f'temp_buf = {temp_buf[0]}')
            print(f'hw_info cpu_freq = {hw_info.get("cpu_freq")}')
        print(f'CPU frequency {core} check'.ljust(40, '.'), end='')
        if hw_info.get('cpu_freq') in temp_buf[0]:
            print('PASSED')
        else:
            print('FAILED')
            sys.exit()
    return


def _check_sw_os_release(verbose):
    stdin, stdout, _ = ssh_client.exec_command('cat /etc/os-release')
    temp_buf = stdout.readlines()
    if verbose:
        print(f'temp_buf = {temp_buf}')
        print(f'os_release = {hw_info.get("os_release")}')

    print(f'OS-Release Version'.ljust(40, '.'), end='')
    if hw_info.get('os_release') in temp_buf[1]:  # check element 1
        print('PASSED')
    else:
        print('FAILED')
        sys.exit()
    return


def _check_sw_kernel(verbose):
    stdin, stdout, _ = ssh_client.exec_command('uname -a')
    temp_buf = stdout.readlines()
    if verbose:
        print(f'temp_buf = {temp_buf}')
        print(f'kernel version = {hw_info.get("kernel")}')

    print(f'Kernel Version'.ljust(40, '.'), end='')
    if hw_info.get('kernel') in temp_buf[0]:  # check first element
        print('PASSED')
    else:
        print('FAILED')
        sys.exit()
    return


def _check_sw_version(verbose):
    stdin, stdout, _ = ssh_client.exec_command('cat /etc/sw-versions')
    temp_buf = stdout.readlines()

    seq = ['buildroot', 'linux', 'uboot']
    for check in seq:
        if verbose:
            print(f'temp_buf = {temp_buf[1]}')
            print(f'SW version {check} = {hw_info.get("sw_version").get(check)}')
        print(f'SW Version {check}'.ljust(40, '.'), end='')
        if hw_info.get('sw_version').get(check) in temp_buf[1]:
            print('PASSED')
        else:
            print('FAILED')
            sys.exit()
        temp_buf.pop(0)
    return


def check_sw(verbose=False):
    """ Check OS, Kernel and SW version """
    print('\nSW Check')

    # Part 1: os-release version
    _check_sw_os_release(verbose)

    # Part 2: Kernel version
    _check_sw_kernel(verbose)

    # Part 3: SW version
    _check_sw_version(verbose)
    return


def check_emmc(verbose=False):
    """ Check eMMC FW and HW revision """
    print('\neMMC Check')
    cmd = 'cat /sys/bus/mmc/devices/mmc0\:0001/fwrev && cat /sys/bus/mmc/devices/mmc0\:0001/hwrev'
    stdin, stdout, _ = ssh_client.exec_command(cmd)
    temp_buf = stdout.readlines()
    seq = ['fw_rev', 'hw_rev']
    for index, check in enumerate(seq):
        if verbose:
            print(f'temp_buf = {temp_buf[index]}')
            print(f'eMMC {check} = {hw_info.get("emmc").get(check)}')
        print(f'eMMC {check}'.ljust(40, '.'), end='')
        if hw_info.get('emmc').get(check) in temp_buf[index]:
            print('PASSED')
        else:
            print('FAILED')
            sys.exit()
    return


def check_temp(verbose=False):
    """ Check current temperature """
    print('\nTemperature Check')
    stdin, stdout, _ = ssh_client.exec_command('cat /sys/class/hwmon/hwmon0/temp1_input')
    temp_buf = stdout.readlines()
    if verbose:
        print(f'temp_buf = {temp_buf}')
    try:
        current_temp = int(temp_buf[0]) / 1000
        print(f'Current temperature: {current_temp}C..............PASSED')
    except ValueError:
        print('Current temperature: Unable to display............FAILED')
        sys.exit()
    return


def check_interface(verbose=False):
    """ Check fan, solenoid, and tachometer symlink file existance """
    print('\nSymlink Check')
    symlink_files = ['/dev/fans', '/dev/solenoids', '/dev/tachometer-0', '/dev/tachometer-1']
    for s_file in symlink_files:
        # cmd = f"python -c \"import os; os.path.islink(\'{s_file}\')\""
        stdin, stdout, _ = ssh_client.exec_command(f'ls {s_file}')
        temp_buf = stdout.readlines()
        if verbose:
            print(f'temp_buf = {temp_buf}')
        print(f'Symlink {s_file} check'.ljust(40, '.'), end='')
        if len(temp_buf) == 0:
            print('FAILED')
            sys.exit()
        print('PASSED')
    return


def clean_up():
    """ Clean up """
    print('\nUUT file clean up')
    stdin, stdout, _ = ssh_client.exec_command(f'rm ~/.ash_history')
    # home_dir = str(Path.home())
    # ssh_dir = home_dir + '/.ssh'
    # file_name = 'known_hosts'
    # t_path = os.path.join(ssh_dir, file_name)
    # os.remove(t_path)
    return


if __name__ == '__main__':
    ssh_connect()
    check_cpu()
    check_cpu_freq()
    check_sw()
    check_emmc()
    check_temp()
    check_interface()
    clean_up()
