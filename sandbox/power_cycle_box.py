#!/home/raylai/anaconda/bin -tt
# !/usr/local/bin/python2.7 -t
import socket
import time
import sys


def switch(ip_value, power_port, status):
    HOST = str(ip_value)  # The remote host IP address
    PORT = 23  # The server port number
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    time.sleep(0.1)  # use time.sleep to give delay and netBooter time to process

    sock.send('\r')  # send \r to start at beginning of line
    time.sleep(0.5)  # delay between commands to allow NP unit to process
    sock.send(' pset %s %s\r' % (power_port, status))
    time.sleep(0.5)

    sock.send('logout\r')  # send logout command to unit to gracefully close socket connection

    # recv = sock.recv(2048)						#receive data from session
    # print(recv)									#print data received

    time.sleep(0.1)

    sock.close()


def reboot(ip_value, power_port):
    HOST = str(ip_value)  # The remote host IP address
    PORT = 23  # The server port number
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    time.sleep(0.1)  # use time.sleep to give delay and netBooter time to process

    sock.send('\r')  # send \r to start at beginning of line
    time.sleep(0.5)  # delay between commands to allow NP unit to process
    sock.send('rb %s\r' % power_port)
    time.sleep(0.5)
    sock.send('logout\r')
    time.sleep(0.1)
    sock.close()


def all_on(ip_value):
    HOST = str(ip_value)  # The remote host IP address
    PORT = 23  # The server port number
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    time.sleep(0.1)  # use time.sleep to give delay and netBooter time to process
    sock.send('\r')  # send \r to start at beginning of line
    time.sleep(0.5)  # delay between commands to allow NP unit to process
    sock.send('ps 1\r')
    time.sleep(0.5)
    sock.send('logout\r')
    time.sleep(0.1)
    sock.close()


def all_off(ip_value):
    HOST = str(ip_value)  # The remote host IP address
    PORT = 23  # The server port number
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    time.sleep(0.1)  # use time.sleep to give delay and netBooter time to process
    sock.send('\r')  # send \r to start at beginning of line
    time.sleep(0.5)  # delay between commands to allow NP unit to process
    sock.send('ps 0\r')
    time.sleep(0.5)
    sock.send('logout\r')
    time.sleep(0.1)
    sock.close()


def reboot_all(ip_value):
    all_off(ip_value)
    time.sleep(10)
    all_on(ip_value)


def env_read(ip_value):
    HOST = str(ip_value)
    PORT = 23
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    time.sleep(0.1)

    sock.send('\r')
    time.sleep(0.3)
    sock.send('cs 1\r')
    time.sleep(0.5)
    recv = sock.recv(2048)
    raw = recv[-155:-6]
    print
    raw
    sock.send('logout\r')
    time.sleep(0.1)
    sock.close()


# print 'PASSED'

def main():
    ip_value = sys.argv[1]  # IP address value entered
    power_port = sys.argv[2]  # Power wanted to be rebooted.
    if power_port == 'env':
        env_read(ip_value)
    else:
        status = sys.argv[3]
        print('Using: \nPower cycle box@: ' + ip_value)
        print('Power cycle port(s): ' + power_port)
        print('Status: ' + status)
        if status == 'reboot':
            if power_port == 'all':
                reboot_all(ip_value)
            else:
                reboot(ip_value, power_port)
        elif status == 'on':
            if power_port == 'all':
                all_on(ip_value)
            else:
                state = '1'
                switch(ip_value, power_port, state)
        elif status == 'off':
            if power_port == 'all':
                all_off(ip_value)
            else:
                state = '0'
                switch(ip_value, power_port, state)
        print
        'PASSED'


if __name__ == '__main__':
    print
    'Power cycle utility verion 3.0 on 09/04/2014'
    print
    'power_cycle  <Unit_IP_Addr>  <power_port: # or all or env for current/temp poll>  <status: on, off, reboot>\r\n'
    print
    'Please use the following option:'
    print
    'power_cycle  10.1.1.87 <1-8>  on'
    print
    'power_cycle  10.1.1.87 all  on '
    print
    'power_cycle  10.1.1.87 <1-8>  off '
    print
    'power_cycle  10.1.1.87 all  off '
    print
    'power_cycle  10.1.1.87 <1-8>  reboot '
    print
    'power_cycle  10.1.1.87 all  reboot'
    print
    'power_cycle  10.1.1.87 env\n'
    try:
        main()
    except:
        print
        'There is some error!!'
        print
        'FAILED'
