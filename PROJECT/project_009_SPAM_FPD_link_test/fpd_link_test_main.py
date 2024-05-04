#!/usr/bin/python3
from fpd_ma import box, centroid, RemoteRegAccess, MarginAnalysis, monitor, process_camera
import RPi.GPIO as GPIO
import numpy as np
import os
import paramiko
# import urllib3.request as url
import requests
import json
from functools import wraps
from dataclasses import dataclass
from datetime import datetime
from time import sleep
from threading import Thread, Lock
from pprint import pprint
from typing import Any


__AUTHOR__ = 'ray.lai@getcruise.com'
__VER__ = '0.1.6'

# UUT parameter
HOST = '10.1.1.2'
PORT = 80
USERNAME = 'root'
PASSWORD = 'robotcar'
CAMERA_LOC = (2, 3)  # Camera is at port 2 and 3

# RPi input/output component BCM location
SWITCH = 2
RELAY = 3

# FPD MA Pass/Fail Criteria
ROW, COLUMN = 3, 4

# Test result template (blank)
TEST_RESULT = {'camera_2': {'0.3m': '', '10m': ''},
               'camera_3': {'0.3m': '', '10m': ''}}

# Sample MA data
DATA = [[-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 1, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, 1, 0, 0, 0, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 0, 1, 1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 0, 1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, -1, -1, -1, -1]]

# Sample Trace data
TRACE = {"api": "/api/v1.0/trace/hwinfo", \
         "hwinfo": {"CruisePN": "1003483", \
                    "GMW15862": {"DUNS": "460062987", \
                                 "GMPN": "1X391433B", \
                                 "TRACE": "1121035BETA10001", \
                                 "VPPS": "8161302000000X"}}, \
         "status": "success"}
"""
Linux command
Stop camera diagnostic process
sv stop fpd-camera-monitor-0

Stop camera server from interfering:
curl http://10.1.1.2/api/v1.0/cppm/cameras/2/attribute/margin_analysis/on
curl http://10.1.1.2/api/v1.0/cppm/cameras/3/attribute/margin_analysis/on

Python-based script: 
python3 fpd_ma.py --host 10.1.1.2 --dwell-time 1 --min-sp -7 --max-sp 7 2 3

"""


@dataclass
class Args:
    cameras: int = CAMERA_LOC
    host: str = HOST
    port: int = PORT
    get_sp_eq: bool = False
    set_strobe: int = -1
    set_eq: int = -1
    dwell_time: float = 1.0
    alt: bool = False
    output_dir: str = None
    min_sp: int = -7
    max_sp: int = 7
    uut_sn: str = ''
    cable_length: str = ''
    ssh: Any = None


def ssh_connect():
    print('Connecting to SPAM UUT...')
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOST, username=USERNAME, password=PASSWORD)
    return ssh_client


def get_uut_sn():
    print('Getting the UUT SN...')
    cmd = f'http://{HOST}:{PORT}/api/v1.0/trace/hwinfo'
    r = requests.get(cmd)

    try:
        if r.status_code == 200:
            uut_sn = r.json().get('hwinfo').get('GMW15862').get('TRACE')
            print(f'UUT TRACE SN: {uut_sn}')
            return uut_sn
    except:
        print('This UUT does not have the correct TRACE information programmed...')
        _print_test_result('FAILED', 'Invalid_UUT')


def camera_diag_stop(ssh):
    print('Stopping camera diag...')
    # cmd = 'sv stop fpd-camera-monitor-0'
    cmd = 'sv stop fpd-camera-monitor'
    _, ssh_stdout, _ = ssh.exec_command(cmd)
    temp_buf = ssh_stdout.readlines()
    print(temp_buf[0].strip('\n'))


def camera_server_stop(action: bool):
    """
    To stop the camera server, action == True
    To start the camera server, action == False
    """
    if action:
        print('Stopping camera server...')
        t = 'on'
    else:
        print('Starting camera server...')
        t = 'off'

    for camera in CAMERA_LOC:
        api_str = f'http://{HOST}:{PORT}/api/v1.0/cppm/cameras/{camera}/attribute/margin_analysis/{t}'
        r = requests.get(api_str)
        sleep(2)
        # print(f'r = {r.json()}')

        if r.status_code != 200:
            print(f'Camera server is already turned off for camera {camera}')


def rpi_gpio_setup():
    print('RPi version: ', GPIO.RPI_INFO)
    print('RPi.GPIO version: ', GPIO.VERSION)
    GPIO.setwarnings(False)  # To not display the GPIO warning messages
    GPIO.setmode(GPIO.BCM)
    # print(f'{GPIO.getmode()}')

    GPIO.setup(SWITCH, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # no initial option for input
    GPIO.setup(RELAY, GPIO.OUT, initial=GPIO.LOW)

    GPIO.add_event_detect(SWITCH, GPIO.FALLING)
    GPIO.output(RELAY, GPIO.LOW)


def run_updated_margin_analysis(args, ma):
    cameras = args.cameras
    use_alt = args.alt
    threads = []

    # print("Before scanning run 'sv stop fpd-camera-monitor-0' on the SPAM")
    print(f'Running FPD test with {args.cable_length} cable')
    print("Scanning...")

    args.output_dir = "ma_" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if not os.path.isdir(args.uut_sn):
        os.mkdir(args.uut_sn)  # structure the test under the SN
    args.output_dir = os.path.join(args.uut_sn, args.output_dir)
    os.mkdir(args.output_dir)  # Now the test result is structured under uut_sn/ma_{timestamp}

    monitor_thread = Thread(target=monitor, args=(ma,))
    monitor_thread.start()

    ma.backup(cameras)

    if use_alt:
        for cam in cameras:
            target = process_camera(args.output_dir, ma, cam, True)
    else:
        for cam in cameras:
            t = Thread(target=process_camera, args=(args.output_dir, ma, cam, False))
            t.start()
            threads.append(t)

    for t in threads:
        t.join()

    ma.stop_monitor = True
    monitor_thread.join()

    ma.restore(cameras)
    print(f"\nDone. Results stored in \"{args.output_dir}\"")


def fpd_link_test_sequence(func):
    """
    This is the decorator for the main test sequence including the RPi GPIO sequence
    """

    @wraps(func)
    def wrapper(*args):
        """ FPD link main test sequence
            func = fpd_link_test_main
        """
        # Run FPD link test - 0.3m cable
        display_current_time('testing')
        func(args)
        post_ma_analysis(args, '0.3m')

        # Enable SSR to switch over to 10m cable
        print('Enable relay; switch to 10m cable for FPD link test...')
        GPIO.output(RELAY, GPIO.HIGH)

        # Run FPD link test - 10m cable
        display_current_time('testing')
        func(args)
        post_ma_analysis(args, '10m')

        # Display overall test result
        display_test_result(args.uut_sn)

        # Disable SSR to switch over back to 0.3m cable
        print('Disable relay; switch back to 0.3m cable for FPD link test...')
        GPIO.output(RELAY, GPIO.LOW)

    return wrapper


# @fpd_link_test_sequence
def fpd_link_test_main(args):
    """
    The FPD link test main is sourced from the fpd_ma.py but with updated run_margin_analysis()
    """
    des_regs = RemoteRegAccess(args.host, args.port)
    ma = MarginAnalysis(des_regs, args.dwell_time, args.min_sp, args.max_sp)
    run_updated_margin_analysis(args, ma)


def uut_setup(seq: str) -> Args:
    # Display starting test
    display_current_time('starting')

    # Create SSH object handle
    ssh = ssh_connect()

    # Stop camera diagnostic process
    camera_diag_stop(ssh)

    # Stop camera server from interfering:
    camera_server_stop(action=True)

    if seq == 'initial_boot':
        # Get UUT trace information
        uut_sn = get_uut_sn()

        # Initialize FPD test variables
        args = Args()
        args.uut_sn = uut_sn

    args.ssh = ssh

    return args


def reboot_spam(args):
    _, _, _ = args.ssh.exec_command('reboot')
    sleep(30)  # Wait for 30 second to boot


def display_current_time(status: str):
    current_status = {'idling': 'The FPD link test station is idling...',
                      'testing': 'The FPD link test is in progress......',
                      'starting': '\n' + '=' * 52 + '\nThe FPD link test is starting.........',
                      'completed': 'The FPD link test is completed........'}
    print(f'{current_status.get(status, "Status parameter input is not correct")}...', end='')
    print('Current time is', datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


def post_ma_analysis(args: Args):
    # Post MA analysis and output the test result to file
    cable_length = args.cable_length
    for camera in CAMERA_LOC:
        print(f'Opening camera log at {args.output_dir}/ma_{camera}.log')
        file_loc = os.path.join(args.output_dir, f'ma_{camera}.log')

        data = os.popen(f'tail -n 16 {file_loc}').read()
        if 'Best setting' not in data:
            print('Test data is corrupted during test... Please rerun the test')
            return

        data = data.split('\n')  # data is the string form of the 2D array
        center = eval(data[-1].strip('Best Setting: '))  # take the last line, strip off the 'Best Setting' and eval the tuple
        new_data = []
        for row in data[:-2]:  # last element is center point
            r = row.strip('[').strip(' [').strip(']')
            r = r.split()
            new_data.append([int(i) for i in r])

        ndata = np.array(new_data)
        print(f'center = {center}')
        corner_pos = box(ndata, center)
        print(f'corner_pos = {corner_pos}')
        row = corner_pos[1][0] - corner_pos[0][0] + 1
        col = corner_pos[1][1] - corner_pos[0][1] + 1
        print(f'Green area is {row} x {col}')

        camera_key = f'camera_{camera}'
        if row >= ROW and col >= COLUMN:
            print(f'Camera {camera} TEST PASSED')
            TEST_RESULT[camera_key][cable_length] = 'PASSED'
        else:
            print(f'Camera {camera} TEST FAILED')
            TEST_RESULT[camera_key][cable_length] = 'FAILED'

        # Save test result in the log
        log_filename = f'{args.output_dir}/TEST_RESULT_{camera}_{cable_length}.log'
        print(f'Saving the test analysis to {log_filename}')
        with open(log_filename, 'w+') as f:
            f.write(f'Testing FPD Link on camera {camera}\n')
            f.write(f'   Cable length = {cable_length}\n')
            f.write(f'   Image center = {center}\n')
            f.write(f'   Corner position = {corner_pos}\n')
            f.write(f'   Green area: {row} x {col}\n')
            f.write(f'   Test result: {TEST_RESULT[camera_key][cable_length]}\n')


def _print_test_result(result: str, uut_sn: str):
    print('=' * 52)
    print(f'Overall FPD link test result for {uut_sn}: ')
    print(f'{result} ' * 7)
    display_current_time('completed')
    print('=' * 52, '\n')


def display_test_result(uut_sn: str):
    pprint(TEST_RESULT)
    overall_test_result = 'PASSED'
    for camera, result_store in TEST_RESULT.items():
        for cable_length, result in result_store.items():
            if TEST_RESULT[camera][cable_length] == 'FAILED':
                overall_test_result = 'FAILED'
    _print_test_result(overall_test_result, uut_sn)


if __name__ == '__main__':
    # Set up RPi GPIO
    rpi_gpio_setup()

    try:
        while True:
            if GPIO.event_detected(SWITCH):
                # UUT setup and initialize
                args = uut_setup(seq='initial_boot')

                # Run FPD link test
                args.cable_length = '0.3m'
                display_current_time('testing')
                fpd_link_test_main(args)
                post_ma_analysis(args)

                # Enable SSR to switch over to 10m cable
                print('Enable relay; switch to 10m cable for FPD link test...')
                GPIO.output(RELAY, GPIO.HIGH)

                # Reboot SPAM
                reboot_spam(args)

                # UUT setup
                args = uut_setup(seq='reboot')

                # Run FPD link test - 10m cable
                args.cable_length = '10m'
                display_current_time('testing')
                fpd_link_test_main(args)
                post_ma_analysis(args)

                # Display overall test result
                display_test_result(args.uut_sn)

                # Disable SSR to switch over back to 0.3m cable
                print('Disable relay; switch back to 0.3m cable for FPD link test...')
                GPIO.output(RELAY, GPIO.LOW)

            else:
                display_current_time('idling')
                sleep(10)

    except KeyboardInterrupt:
        print('\nExiting the script...')

    finally:
        GPIO.output(RELAY, GPIO.LOW)
        GPIO.cleanup()
