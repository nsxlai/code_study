IP_ADDR = '10.1.1.2'
PORT = '80'
API_VER = 'v1.0'
API_HEADER = f'http://{IP_ADDR}:{PORT}/api/{API_VER}'

spam_dut = {
    'username': 'root',
    'password': 'robotcar',
    'bank_0_ports': [0, 1, 2, 3],
    'bank_1_ports': [4, 5, 6, 7],
    'solenoid_on': {'api': f'{API_HEADER}/spam/solenoid_on',
                    'desc': 'Turning on solenoid port'},
    'solenoid_off': {'api': f'{API_HEADER}/spam/solenoid_off',
                     'desc': 'Turning off solenoid port'},
    'fan_speed_set': {'api': f'{API_HEADER}/spam/fan_speed/set',
                      'desc': 'Setting fan speed'},
    'fan_on': {'api': f'{API_HEADER}/spam/fan_on',
               'desc': 'Turning on fan'},
    'fan_off': {'api': f'{API_HEADER}/spam/fan_off',
                'desc': 'Turning off fan'},
    'hwinfo': {'api': f'{API_HEADER}/trace/hwinfo',
               'desc': 'Display HW information'},
    'swinfo': {'api': f'{API_HEADER}/swupdate/sw-versions/rootfs',
               'desc': 'Display SW information'},
    'cpuinfo': {'api': f'{API_HEADER}/spam/cpu_check/lscpu',
                'desc': 'Display CPU information'},
    'iperf_svr': {'cmd': 'iperf3 -s -D',
                  'desc': 'Start IPERF server at port'},
    'traffic': {'send': {'port': 5201, 'log': 'iperf_send_log.txt'},
                'recv': {'port': 5202, 'log': 'iperf_recv_log.txt'},
                'gbits/sec': {'upper_limit': 1.1, 'lower_limit': 0.9},
                'mbits/sec': {'upper_limit': 1100, 'lower_limit': 830},
                'retr_limit': 10,
                },
    'temp': {'cmd': '/usr/sbin/spamtest_i2c_sht31',
             'desc': 'Local command for getting temperature and humidity raw hex value'},
    'stress': {'cmd': 'stress-ng --memrate 12 --cpu 2 --timeout',
               'desc': 'Standard Linux stress NG utility using memrate to test CPU/DRAM',
               'log': 'stress_log.txt'},
    'rpi': {'ip_addr': {'set_cmd': 'sudo ifconfig eth0 10.1.1.1 netmask 255.0.0.0',
                        'desc': 'Setup the RPi Eth0 IP address',
                        'chk_cmd': 'ifconfig eth0'},
            'routing_table': {'set_cmd': 'sudo ip route add 10.1.1.0/24 dev eth0',
                              'desc': 'Setup the RPi routing table',
                              'chk_cmd': 'ip route'},
            },

}
