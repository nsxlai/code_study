import paramiko
import json
from time import sleep, time
from datetime import datetime
from threading import Thread


__AUTHOR__ = 'ray.lai@getcruise.com'
__VER__ = '0.2.2'


# PARAMETER
HOST = '10.1.1.2'
USERNAME = 'root'
PASSWORD = 'robotcar'
POLL_INTERVAL = 2  # Poll status every second
CAMERA_LOC = (False, True)  # First element is camera at port 2 and second is camera at port 3
LOG_DIR = '/tmp/'


def ssh_connect():
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname=HOST, username=USERNAME, password=PASSWORD)
    return ssh_client


class FPD:
    def __init__(self):
        self.ssh = ssh_connect()
        self.pid = None
        self.dt = None  # test start datetime
        self.test_metrics = {}

    def _send_cmd(self):
        cmd = f'{self.test_metrics.get("cmd", None)} > {LOG_DIR}{self.log_filename} &'
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
        sleep(2)

    def _get_pid(self):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(
            f"ps -ef | grep \'{self.test_metrics.get('cmd', '')}\'")
        temp_buf = ssh_stdout.readlines()
        self.pid = temp_buf[0].split()[0]
        # print(self.pid)

    def _fetch_data(self) -> dict:
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(
            f'tail -n {self.test_metrics.get("obj_len", 0)} /tmp/{self.log_filename}')
        temp_buf = ssh_stdout.readlines()
        temp_buf = ''.join(temp_buf)
        data = json.loads(temp_buf)
        # print(data)
        return data

    def _camera_port_check(self, measurement):
        """
        If the camera is not installed (False on the CAMERA_LOC), the result will be 0
        """
        port_2_result = measurement[0] * CAMERA_LOC[0]
        port_3_result = measurement[1] * CAMERA_LOC[1]
        return [port_2_result, port_3_result]

    def execute(self):
        """
        To not fill up the small storage space in SPAM, the script will restart the FPD commands every 10 minutes
        """
        self.dt = datetime.now()  # Human-readable date time data
        print(f'test started on {self.dt:%b}-{self.dt:%d}-{self.dt:%Y} {self.dt:%H}:{self.dt:%M}:{self.dt:%S}')
        while True:
            start_time = int(time())
            self._send_cmd()
            self._get_pid()
            while (int(time()) - start_time) < 600:  # Will exit the loop after 10 minutes (600 seconds)
                json_data_obj = self._fetch_data()
                self.error_check(json_data_obj)
                print(f"{json_data_obj['header']['name']}--{json_data_obj['header']['timestamp']}")
                sleep(POLL_INTERVAL)
            print('10 minutes has elapsed...')
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(f'kill {self.pid}')

    def close(self):
        ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(f'kill {self.pid}')
        sleep(1)
        self.ssh.close()


class FPDCameraMonitor(FPD):
    def __init__(self):
        super().__init__()
        self.test_metrics = {'log_filename': 'fpd_camera_monitor.log', 'obj_len': 272,
                             'key_metrics': ['SER_953_CRC_ERR_CNT', 'SER_953_CSI_ERR_CNT',
                                             'SER_953_CSI_ERR_STATUS_REG'],
                             'frame_count': 'DESER_960_IND_CSI0TX_FRM_CT',
                             'cmd': 'cruise-edd-monitor-listen.py --name fpd_camera'}
        self.log_filename = self.test_metrics['log_filename']

    def error_check(self, json_data_obj: dict):
        error_flag = False
        # test 1
        if json_data_obj['header']['errNo'] != 'Ok':
            print('CameraMonitor status is NOT OK')
            error_flag = True

        # test 2
        measurements = json_data_obj['measurements']
        for key in self.test_metrics['key_metrics']:
            if self._camera_port_check(measurements[key]) != [0, 0]:
                print(f'{key} is NOT OK ({measurements[key]})')
                error_flag = True

        # test 3
        faultCounters = json_data_obj['faultCounters']
        for fault_name, fault_value in faultCounters.items():
            if type(fault_value) == list:
                if self._camera_port_check(fault_value) != [0, 0]:
                    print(f'{fault_name} is NOT OK ({fault_value})')
                    error_flag = True
            elif type(fault_value) == int:
                if fault_value != 0:
                    print(f'{fault_name} is NOT OK ({fault_value})')
                    error_flag = True

        if error_flag:
            print('-' * 50)
            frame_count = int(measurements.get(self.test_metrics.get('frame_count')))
            print(f"Frame count = {frame_count}")
            if frame_count == 0:
                print(f'Camera has STOPPED streaming...')
                cur_dt = datetime.now()
                print(f'Error detected on {cur_dt:%b}-{cur_dt:%d}-{cur_dt:%Y} {cur_dt:%H}:{cur_dt:%M}:{cur_dt:%S}')
            else:
                print(f'Camera has resumed streaming...')
            print('-' * 50)
            # raise ValueError(f'Check {self.test_metrics["log_filename"]} log: {json_data_obj["header"]}')


class FPDCameraVideoStreamStats(FPD):
    def __init__(self):
        super().__init__()
        self.test_metrics = {'log_filename': 'fpd_camera_video_stream_stats.log', 'obj_len': 281,
                             'key_metrics': ['error_flags', 'total_row_crc_error_count',
                                             'total_frame_geometry_error_count', 'total_frame_timeout_count'],
                             'cmd': 'cruise-edd-monitor-listen.py --name fdp_camera_video_stream_stats'}
        self.log_filename = self.test_metrics['log_filename']

    def error_check(self, json_data_obj: dict):
        error_flag = False
        # test 1
        if json_data_obj['header']['errNo'] != 'Ok':
            print('CameraVideoStream status is NOT OK')
            error_flag = True

        # test 2
        measurements = json_data_obj['measurements']
        for key in self.test_metrics['key_metrics']:
            if self._camera_port_check(measurements[key]) != [0, 0]:
                print(f'{key} is NOT OK ({measurements[key]})')
                error_flag = True

        if error_flag:
            cur_dt = datetime.now()
            print(f'Error detected on {cur_dt:%b}-{cur_dt:%d}-{cur_dt:%Y} {cur_dt:%H}:{cur_dt:%M}:{cur_dt:%S}')
            #  raise ValueError(f'Check {self.test_metrics["log_filename"]} log: {json_data_obj["header"]}')


def video_traffic_start():
    global c1, c2
    c1 = FPDCameraMonitor()
    c2 = FPDCameraVideoStreamStats()
    thread1 = Thread(target=c1.execute, args=())
    thread2 = Thread(target=c2.execute, args=())
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()


if __name__ == '__main__':
    try:
        # video_traffic_start()
        c1 = FPDCameraMonitor()
        c1.execute()
    except KeyboardInterrupt:
        print('Exiting the script...')

    finally:
        c1.close()
        # c2.close()
        print('-' * 50)
        cur_dt = datetime.now()
        print(f'Test started on {c1.dt:%b}-{c1.dt:%d}-{c1.dt:%Y} {c1.dt:%H}:{c1.dt:%M}:{c1.dt:%S}')
        print(f'Current time is {cur_dt:%b}-{cur_dt:%d}-{cur_dt:%Y} {cur_dt:%H}:{cur_dt:%M}:{cur_dt:%S}')
