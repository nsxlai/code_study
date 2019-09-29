"""
Please write a basic test framework that has the following architecture:
A top level class that has:
    i. A logging function that writes log messages to stdout/stderr and a file

   ii. A tcp client function (ie, returns a web page or interacts with a simple stub tcp server
      just returns some text for the caller to parse, nothing complicated)

  iii. Has mandatory init fields of serial_number and part_number

2 subclasses :
    i. ProductA :
       1. get_data_1 function that calls tcp client function and parses out expected text using regex,
          returning all matches in a List
       2. create a decorator for get_data_1 that logs some text with a formatted timestamp each time it’s run

   ii. ProductB :
       1. get_data_2 function that does the same thing for parsing out all words in the text as a dictionary like
          { word1: word2, word3: word4, etc }

Add exception handling such that correct error messages are presented when :
    a. Serial number does not match a pre-compiled regex pattern
    b. Get_data_1 text is not found
    c. Get_data_2 keys do not contain duplicate words
    d. Raise an exception if the TCP client in the top level class cannot connect – what are the variants here?
       Don’t bother coding them all, just handle 1 and list what you would handle in a fully functional framework.

Catch this exception in get_data_2 such that it retries twice before propagating that exception
ie, if it fails once then passes, the test should continue

3. Make the class file executable so that you can run the file stand alone
4. Create a pytest for get_data_1 that uses mock to simulate the tcp client function –
   2 basic sample tests, one positive, one negative
5. Create a separate script that creates 10 objects of the top level class.
6. Create a new list using list comprehension that only contains objects with an odd numbered serial number.
"""


import socket
import sys
from time import time, localtime
import re
import functools
from random import randint


HOST = 'localhost'
PORT = 5050


def time_logging(func):
    '''Decorator function that calculate the function run time'''
    @functools.wraps(func)
    def wrapper(*args):
        t0 = time()
        data_out = func(*args)
        t1 = time()
        elapsed_time = t1 - t0
        print(f'Run time: {elapsed_time}')
        return data_out
    return wrapper


class GetData1Error(Exception):
    '''Custom exception for ProductA get_data_1'''
    pass


class GetData2Error(Exception):
    '''Custom exception for ProductB get_data_2'''
    pass


class BaseProduct:
    '''Define the base property'''

    def __init__(self, serial_number, product_number):
        """
        The constructor will take in user input serial number and product number and also check
        the validity of the serial number with a specific regex pattern
        :param serial_number: Follow the regex format: 3 alpha characters follow by 8 alpha-numeric characters
        :param product_number: Product ID
        """
        self.serial_number = serial_number
        self.product_number = product_number
        sn_regex_pattern = r'^[A-Z]{3}[A-Z0-9]{8}$'
        sn_check = re.match(sn_regex_pattern, serial_number)
        if sn_check is None:
            raise ValueError('The serial number format is not correct!!')

    def tcp_connect_cm(self, server_ip_addr, server_port, command):
        """
        The method will use the context manager to provide the TCP socket connectivity and check for connection error
        :param server_ip_addr: Server IP address (str)
        :param server_port: Server port (int)
        :param command: Command issues to interact with the server
        :return: data: Output from the server
        """
        server_addr = (server_ip_addr, server_port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(server_addr)
                sock.sendall(str.encode(command))  # Encode str to byte format
                data = sock.recv(1024)
                data = data.decode()               # Decode byte format back to str
                self.logging(data, '')
                return data
            except ConnectionRefusedError as CRE:  # If
                error_str = 'Unable to connect to the server!!'
                print(error_str)
                self.logging('', error_str)
                sys.exit(0)

    def logging(self, stdout_msg='', stderr_msg=''):
        """
        Redirect the msg to either sys.stdout and sys.stderr
        Also log the message to a file
        :param stdout_msg: string output for sys.stdout
        :param stderr_msg: string output for sys.stderr
        :return: None
        """
        if stdout_msg:
            print(f'stdout message: {stdout_msg}', file=sys.stdout)
        if stderr_msg:
            print(f'stderr message: {stderr_msg}', file=sys.stderr)

        # Need to create local log for message output. Will use standard
        # file name 'product_data' and with a local time suffix to give
        # the uniqueness of the file name.
        freeze = localtime()
        year = freeze.tm_year
        month = freeze.tm_mon
        day = freeze.tm_mday
        hour = freeze.tm_hour
        min = freeze.tm_min
        sec = freeze.tm_sec
        file_suffix = f'{year}{month}{day}_{hour}{min}{sec}'
        with open(f'product_data_{file_suffix}.log', 'w') as f:
            f.write(stdout_msg)
            f.write(stderr_msg)

    def product_display(self):
        return 'Product Number = {}; Serial Number = {}'.format(self.product_number, self.serial_number)


class ProductA(BaseProduct):
    @time_logging
    def get_data_1(self, server_ip_addr, server_port, command, regex_str):
        data = super().tcp_connect_cm(server_ip_addr, server_port, command)
        regex_output = re.findall(regex_str, data)
        if not regex_output:  # No output
            raise GetData1Error('No output from ProductA.get_data_1')
        return regex_output


class ProductB(BaseProduct):
    def get_data_2(self, server_ip_addr, server_port, command):
        counter = 0
        while counter <= 3:  # will return the tcp_connect_cm twice before return GetData2Error
            data = super().tcp_connect_cm(server_ip_addr, server_port, command)
            print(f'data = {data}')
            if not data and counter > 2:  # For the case if there is no output from the server
                raise GetData2Error('No output from ProductB.get_data_2')
            elif data:
                break  # If data has value, break out of the while loop
            counter += 1
            print(f'counter = {counter}')
        data = data.split()
        i = 0
        test_dict = {}
        tail_value = None
        if len(data) % 2 != 0:       # If data has odd elements,
            tail_value = data.pop()  # store the last element and insert into the dictionary later
        while i < len(data):
            if len(data) != 0:  # In case data only has 1 element, the element will be popped to tail_val at this point
                if data[i] in test_dict:
                    data[i] = data[i] + '_' + str(randint(0, 100))  # in case of duplicating keys, will add a randomized
                test_dict[data[i]] = data[i+1]                      # integer suffix at the end of the key
                i = i + 2
        if tail_value:
            test_dict[tail_value] = ''  # Assign empty string for placeholder
        return test_dict


if __name__ == '__main__':
    try:
        # uut_01_sn = 'ROC11111111'
        # uut_01_pn = 'POWER-001A'
        # uut_01 = ProductA(uut_01_sn, uut_01_pn)
        # # print(uut_01.product_display())
        # sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_01_pn} \n Serial_Num: {uut_01_sn} \n EOL'
        # uut_01_output = uut_01.tcp_connect_cm(HOST, PORT, sim_server_output)
        # print(f'received: {uut_01_output}')

        uut_02_sn = 'ROC12345HKK'
        uut_02_pn = 'POWER-002A'
        uut_02 = ProductA(uut_02_sn, uut_02_pn)
        sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_02_pn} \n Serial_Num: {uut_02_sn} \n EOL'
        uut_02_output = uut_02.get_data_1(HOST, PORT, sim_server_output, 'Num')
        print(f'received: {uut_02_output}')

        # uut_03_sn = 'ROC212330L5'
        # uut_03_pn = 'POWER-001B'
        # uut_03 = ProductB(uut_03_sn, uut_03_pn)
        # # print(UUT_03.product_display())
        # sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_03_pn} \n Serial_Num: {uut_03_sn} \n EOL'
        # uut_03_output = uut_03.get_data_2(HOST, PORT, sim_server_output)
        # print(f'received: {uut_03_output}')

    except ValueError as ve:   # In case of the SN format is not correct
        print(ve)
    except GetData1Error:
        print('No output from ProductA.get_data_1')
    except GetData2Error:
        print('No output from ProductB.get_data_2')

