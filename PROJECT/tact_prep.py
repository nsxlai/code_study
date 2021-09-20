import os
from datetime import datetime


TARGET_DIR = 'c:\\Users\\nsxla\\Documents'

current = datetime.now()
date_folder = f'{current.year}_{current.month}_{current.day}'
time_folder = f'{current.hour}_{current.minute}'
tact_header = 'TACT'

sn_prefix = 'C_'  # TODO: always 3 digits?
sensor_mfg_year = 2021


if __name__ == '__main__':
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

    ans = input('Show current info? (Y/n) ').lower()
    if ans in ['y', 'yes']:
        print(f'Current sensor info:')
        for sensor_num, files in file_dict.items():
            print(f'Sensor {sensor_num}:')
            for file in files:
               print(f'    {file}')

    # Start creating directories:
    temp_dir = os.path.join(TARGET_DIR, date_folder)
    if not os.path.isdir(temp_dir):
        print(f'Creating date folder {date_folder}...')  # TODO: ask for the date format yyyy_mm_dd or yyyy_m_d
        os.mkdir(temp_dir)

    temp_dir = os.path.join(temp_dir, time_folder)
    print(f'Creating run time folder {time_folder}...')
    os.mkdir(temp_dir)

    for file_dir, files in file_dict.items():
        temp_file_dir = os.path.join(temp_dir, file_dir)
        os.mkdir(temp_file_dir)
        os.chdir(temp_file_dir)
        for file_ in files:
            with open(file_, 'w') as f:
                pass

    print('File creation is completed...')
