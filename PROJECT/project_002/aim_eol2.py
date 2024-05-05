#!/home/ray.lai/cruise/dev/bin/python
import paramiko
import sys


HOST = '10.5.40.14'
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
           'os_release': 'VERSION=2020.02.1-g6e1966d216',
           'kernel': '5.4.0',
           'sw_version': {'rootfs': '0.8.0-5a0f125853d22abc7583f9f116513409ae4a00a5',
                          'buildroot': '6e1966d216dea6d0c2e155bbe1c26a7687023876',
                          'linux': 'xilinx-v2020.2-cruise.11',
                          'uboot': 'xilinx-v2020.2-cruise.2',
                          'vivado_fw': '0.0.1-57d37952c9675786eaac926d426161455a85cd11',
                          'build_type': 'eng'},
           'emmc': {'fw_rev': '0x3339313032343137',
                    'hw_rev': '0x0'},
           'temp': {'low_limit': 26, 'high_limit': 37},
           'voltage_rails': {'voltage0_rail_vccint': {'nominal': 0.850,
                                                      'low_limit': 0.80,
                                                      'high_limit': 0.90,
                                                      'multiplier': 1,
                                                      'name': 'vccint'},
                             'voltage1_rail_vccaux': {'nominal': 1.800,
                                                      'low_limit': 1.75,
                                                      'high_limit': 1.85,
                                                      'multiplier': 1,
                                                      'name': 'vccaux'},
                             'voltage2_rail_vccbram': {'nominal': 0.850,
                                                       'low_limit': 0.80,
                                                       'high_limit': 0.90,
                                                       'multiplier': 1,
                                                       'name': 'vccbram'},
                             'voltage3_rail_vccpsintlp': {'nominal': 0.850,
                                                          'low_limit': 0.80,
                                                          'high_limit': 0.90,
                                                          'multiplier': 1,
                                                          'name': 'vccpsintlp'},
                             'voltage4_rail_vccpsintfp': {'nominal': 0.850,
                                                          'low_limit': 0.80,
                                                          'high_limit': 0.90,
                                                          'multiplier': 1,
                                                          'name': 'vccpsintfp'},
                             'voltage5_rail_vccpsaux': {'nominal': 1.800,
                                                        'low_limit': 1.75,
                                                        'high_limit': 1.85,
                                                        'multiplier': 1,
                                                        'name': 'vccpsaux'},
                             'voltage6_rail_vrefp': {'nominal': 1.800,
                                                     'low_limit': 1.20,
                                                     'high_limit': 1.30,
                                                     'multiplier': 1,
                                                     'name': 'vrefp'},
                             'voltage7_rail_vrefn': {'nominal': 0,
                                                     'low_limit': -0.05,
                                                     'high_limit': 0.05,
                                                     'multiplier': 1,
                                                     'name': 'vrefn'},
                             'voltage8_rail': {'nominal': 9.0,
                                               'low_limit': 0.924609375,
                                               'high_limit': 0.938671875,
                                               'multiplier': 9.66,
                                               'name': 'P9V0_A2B_TACT'},
                             'voltage9_rail': {'nominal': 9.0,
                                               'low_limit': 0.924609375,
                                               'high_limit': 0.938671875,
                                               'multiplier': 9.66,
                                               'name': 'P9V0_A2B_FP'},
                             'voltage10_rail': {'nominal': 12.0,
                                                'low_limit': 0.45,
                                                'high_limit': 0.861328125,
                                                'multiplier': 21.00,
                                                'name': 'P12V0_BATT_MON'},
                             'voltage11_rail': {'nominal': 1.2,
                                                'low_limit': 0.896484375,
                                                'high_limit': 0.924609375,
                                                'multiplier': 1.32,
                                                'name': 'P1V2_DDR4_MON'},
                             'voltage12_rail': {'nominal': 0.9,
                                                'low_limit': 0.8859375,
                                                'high_limit': 0.9140625,
                                                'multiplier': 1,
                                                'name': 'P0V9_MGTAVCC_MON'},
                             'voltage13_rail': {'nominal': 1.2,
                                                'low_limit': 0.896484375,
                                                'high_limit': 0.924609375,
                                                'multiplier': 1.32,
                                                'name': 'P1V2_MON'},
                             'voltage14_rail': {'nominal': 0.85,
                                                'low_limit': 0.83671875,
                                                'high_limit': 0.861328125,
                                                'multiplier': 1,
                                                'name': 'P0V85_PSMGTRAVCC_MON'},
                             'voltage15_rail': {'nominal': 2.5,
                                                'low_limit': 0.8578125,
                                                'high_limit': 0.882421875,
                                                'multiplier': 2.86,
                                                'name': 'P2V5_DDR4_MON'},
                             'voltage16_rail': {'nominal': 1.8,
                                                'low_limit': 0.8859375,
                                                'high_limit': 0.910546875,
                                                'multiplier': 2,
                                                'name': 'P1V8_IO_VCCO_MON'},
                             'voltage17_rail': {'nominal': 0.6,
                                                'low_limit': 0.5765625,
                                                'high_limit': 0.622265625,
                                                'multiplier': 1,
                                                'name': 'P0V6_VTT_MON'},
                             'voltage18_rail': {'nominal': 3.3,
                                                'low_limit': 0.896484375,
                                                'high_limit': 0.92109375,
                                                'multiplier': 3.67,
                                                'name': 'P3V3_SYS_MON'},
                             'voltage19_rail': {'nominal': 5.0,
                                                'low_limit': 0.85078125,
                                                'high_limit': 0.889453125,
                                                'multiplier': 5.75,
                                                'name': 'P5V0_SYS_MON'},
                             'voltage20_rail': {'nominal': 1.8,
                                                'low_limit': 0.8859375,
                                                'high_limit': 0.910546875,
                                                'multiplier': 2,
                                                'name': 'P1V8_ETH_MON'},
                             'voltage21_rail': {'nominal': 0.9,
                                                'low_limit': 0.8859375,
                                                'high_limit': 0.9140625,
                                                'multiplier': 1,
                                                'name': 'P0V9_ETH_MON'},
                             'voltage22_rail': {'nominal': 0.85,
                                                'low_limit': 0.418359375,
                                                'high_limit': 0.432421875,
                                                'multiplier': 2,
                                                'name': 'P0V85_PSINTLP_VCC_MON'},
                             'voltage23_rail': {'nominal': 1.8,
                                                'low_limit': 0.8859375,
                                                'high_limit': 0.910546875,
                                                'multiplier': 1,
                                                'name': 'P1V8_PS_MGTRAVTT_MON'},
                             }
           }


def ssh_connect():
    print('Initiating SSH connection...')
    global ssh_client
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOST, username=USERNAME, password=PASSWORD, look_for_keys=False, allow_agent=False)


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


def _create_linux_device_name(name: str) -> tuple:
    """ Supplementary function that create the Linux device name from the given voltage rail """
    rail = name.split('_')
    if len(rail) == 3:  # rail number and name are included in the input name
        raw = f'in_{rail[0]}_{rail[2]}_raw'
        scale = f'in_{rail[0]}_{rail[2]}_scale'
    else:
        raw = f'in_{rail[0]}_raw'
        scale = f'in_{rail[0]}_scale'
    return raw, scale


def check_voltage_rail(verbose=False):
    """ Check FPGA voltage rail monitor """
    print('\nVoltage Rail Check')
    dir_path = '/sys/bus/iio/devices/iio:device0'
    voltage_rails = hw_info.get('voltage_rails')
    for voltage_rail in voltage_rails:
        raw, scale = _create_linux_device_name(voltage_rail)
        cmd = f'cat {dir_path}/{raw} && cat {dir_path}/{scale}'
        stdin, stdout, _ = ssh_client.exec_command(cmd)
        temp_buf = stdout.readlines()
        rail_vout = int(temp_buf[0].strip('\n')) * float(
            temp_buf[1].strip('\n')) / 1000  # multiply temp_buf output together
        if verbose:
            print(f'voltage_rail = {voltage_rail}, temp_buf = {temp_buf}, rail_vout = {rail_vout}')

        low_limit = voltage_rails.get(voltage_rail).get('low_limit')
        high_limit = voltage_rails.get(voltage_rail).get('high_limit')
        print(f'{voltage_rail} check'.ljust(40, '.'), end='')
        if not low_limit < rail_vout < high_limit:
            print('FAILED')
            sys.exit()
        print('PASSED')
    return


def check_i2c_temp(verbose=False):
    """ Check on-board I2C temp sensors readout """
    print('\nI2C Temp Sensors Readout')
    low_limit = hw_info.get('temp').get('low_limit')
    high_limit = hw_info.get('temp').get('high_limit')
    for i in range(9):
        cmd = f'cat /sys/class/hwmon/hwmon{i}/temp1_input'
        stdin, stdout, _ = ssh_client.exec_command(cmd)
        temp_buf = stdout.readlines()
        temperature = int(temp_buf[0].strip('\n')) / 1000
        if verbose:
            print(f'Sensor {i} temperature: {temperature:6.2f}C')

        print(f'I2C temp sensor {i} check'.ljust(40, '.'), end='')
        if not low_limit < temperature < high_limit:
            print('FAILED')
            sys.exit()
        print('PASSED')
    return


def check_fpga_temp(verbose=False):
    """ Check FPGA temp sensor readout """
    print('\nFPGA Temp Sensor Readout')
    limit_offset = 10  # FPGA is going to register hotter temp than the I2C ones
    low_limit = hw_info.get('temp').get('low_limit') + limit_offset
    high_limit = hw_info.get('temp').get('high_limit') + limit_offset

    dir_path = '/sys/bus/iio/devices/iio:device0'
    cmd = f'cat {dir_path}/in_temp0_offset && cat {dir_path}/in_temp0_raw && cat {dir_path}/in_temp0_scale'
    stdin, stdout, _ = ssh_client.exec_command(cmd)
    temp_buf = stdout.readlines()
    offset, raw, scale = temp_buf
    offset, raw, scale = offset.strip('\n'), raw.strip('\n'), scale.strip('\n')
    temperature = (int(raw) + int(offset)) * float(scale) / 1000
    if verbose:
        print(f'FPGA temp sensor temperature: {temperature:6.2f}C')

    print(f'FPGA temp sensor check'.ljust(40, '.'), end='')
    if not low_limit < temperature < high_limit:
        print('FAILED')
        sys.exit()
    print('PASSED')
    return


def clean_up():
    """ Clean up """
    print('\nUUT file clean up')
    stdin, stdout, _ = ssh_client.exec_command(f'rm ~/.ash_history')
    return


if __name__ == '__main__':
    ssh_connect()
    check_cpu()
    check_cpu_freq()
    check_sw()
    check_emmc()
    check_voltage_rail()
    check_i2c_temp()
    check_fpga_temp()
    clean_up()
