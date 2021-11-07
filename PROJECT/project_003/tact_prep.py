"""
To run this code, need to install Python 3.x
  - Windows: Install the latest Python from the Windows Store App
  - Linux: sudo pip install python3
  - MAC: should have already came with the OS; use Terminal app to run the program.

Launch the terminal program and change directory to the location of this script file and either one of the following:
  python tact_prep.py
  python3 tact_prep.py

This code will take the user sensor input:
  - Sensor number
  - Sensor serial number
  - sensor MFG month
  - sensor MFG day

and create the date_folder/time_folder for the test run. First set the TARGET_DIR for the directory the test result
is going to (provided example path for Windows, MAC, and Linux. For example, running this test on sensor 1 with
serial number C_011 with MFG date 2021/07/10 on 2021/08/20 at 6:31 PM will create the following file structure:

/User/lab_user1/Documents
    --> 2021_8_20
        --> 18_31
            --> 1
                --> TACT1_C_011_2021010_1G_x.wav
                --> TACT1_C_011_2021010_1G_y.wav
                --> TACT1_C_011_2021010_1G_z.wav

Example user input screen:
What is the TACT sensor number? (1-8): 1
What is the TACT sensor serial number? C_011
What is the TACT sensor MFG month? (1-12): 5
What is the TACT sensor MFG day? (1-31): 40
MFG date input not valid. Input again? (Y/n)
What is the TACT sensor MFG month? (1-12): 5
What is the TACT sensor MFG day? (1-31): 4
Continue to enter info for the next sensor? (Y/n) y
What is the TACT sensor number? (1-8): 2
What is the TACT sensor serial number? C_022
What is the TACT sensor MFG month? (1-12): 3
What is the TACT sensor MFG day? (1-31): 45
MFG date input not valid. Input again? (Y/n)
What is the TACT sensor MFG month? (1-12): 3
What is the TACT sensor MFG day? (1-31): 5
Continue to enter info for the next sensor? (Y/n) y
What is the TACT sensor number? (1-8): 3
What is the TACT sensor serial number? C_033
What is the TACT sensor MFG month? (1-12): 7
What is the TACT sensor MFG day? (1-31): 8
Continue to enter info for the next sensor? (Y/n) y
What is the TACT sensor number? (1-8): 2
What is the TACT sensor serial number? C_033
What is the TACT sensor MFG month? (1-12): 5
What is the TACT sensor MFG day? (1-31): 6
Continue to enter info for the next sensor? (Y/n) n
Show current info? (Y/n) y
Current sensor info:
Sensor 1:
    TACT1_C_011_20210504_1G_x.wav
    TACT1_C_011_20210504_1G_y.wav
    TACT1_C_011_20210504_1G_z.wav
Sensor 2:
    TACT2_C_033_20210506_1G_x.wav
    TACT2_C_033_20210506_1G_y.wav
    TACT2_C_033_20210506_1G_z.wav
Sensor 3:
    TACT3_C_033_20210708_1G_x.wav
    TACT3_C_033_20210708_1G_y.wav
    TACT3_C_033_20210708_1G_z.wav
Creating run time folder 11_37...
File creation is completed...
"""
import os
from datetime import datetime

# For Windows OS:
# TARGET_DIR = 'c:\\Users\\nsxla\\Documents'

# For Linux/MAC OS:
TARGET_DIR = '/Users/ray.lai/Documents'

sn_prefix = 'C_'
sensor_mfg_year = 2021

# ------- DO NOT CHANGE --------
__AUTHOR__ = 'ray.lai@getcruise.com'
current = datetime.now()
date_folder = f'{current.year}_{current.month}_{current.day}'
time_folder = f'{str(current.hour).zfill(2)}_{str(current.minute).zfill(2)}'
tact_header = 'TACT'


def data_ingestion() -> dict:
    file_dict = {}

    while True:
        sensor_num = input('What is the TACT sensor number? (1-8): ')
        sensor_sn = input('What is the TACT sensor serial number? C_')

        while True:
            try:
                sensor_mfg_month = input('What is the TACT sensor MFG month? (1-12): ')
                sensor_mfg_day = input('What is the TACT sensor MFG day? (1-31): ')
                date_check = datetime(int(sensor_mfg_year), int(sensor_mfg_month), int(sensor_mfg_day))
                break
            except (ValueError, TypeError):
                ans = input('MFG date input not valid. Input again? (Y/n) ').lower()
                if ans in ['n', 'no']:
                    break
                continue

        sensor_mfg_date = f'{sensor_mfg_year}{sensor_mfg_month.zfill(2)}{sensor_mfg_day.zfill(2)}'
        file_list = []
        for axis in ['x', 'y', 'z']:
            sensor_file_name = f'TACT{sensor_num}_{sn_prefix}{sensor_sn}_{sensor_mfg_date}_1G_{axis}.wav'
            file_list.append(sensor_file_name)

        file_dict[sensor_num] = file_list

        ans = input('Continue to enter info for the next sensor? (Y/n) ').lower()
        if ans in ['n', 'no']:
            break
        continue
    return file_dict


def show_info(file_dict: dict) -> None:
    ans = input('Show current info? (Y/n) ').lower()
    if ans in ['y', 'yes']:
        print(f'Current sensor info:')
        for sensor_num, files in file_dict.items():
            print(f'Sensor {sensor_num}:')
            for file in files:
                print(f'    {file}')


def create_file_struc(file_dict: dict) -> None:
    temp_dir = os.path.join(TARGET_DIR, date_folder)
    print()
    if not os.path.isdir(temp_dir):
        print(f'Creating date folder {date_folder}...')
        os.mkdir(temp_dir)

    temp_dir = os.path.join(temp_dir, time_folder)
    print(f'Creating run time folder {date_folder}/{time_folder}...')
    os.mkdir(temp_dir)

    for file_dir, files in file_dict.items():
        temp_file_dir = os.path.join(temp_dir, file_dir)
        os.mkdir(temp_file_dir)
        os.chdir(temp_file_dir)
        for file_ in files:
            with open(file_, 'w') as f:
                pass
    print('File creation is completed...')


if __name__ == '__main__':

    # User input data and create file_dict
    file_dict = data_ingestion()

    # Show info?
    show_info(file_dict)

    # Start creating directories:
    create_file_struc(file_dict)
