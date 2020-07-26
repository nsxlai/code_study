"""
This python script will do the following:
    1. open a file
    2. extract email addresses
    3. replace the email addresses from the original message with 'name@abc.com'
    4. output the result to a file
"""
import re
import sys
import os
from time import time, sleep


def function_timer(func):
    def wrapper(infile):
        t0 = time()
        func
        t1 = time()
        elapse_time = (t1 - t0) * 1000000  # elapse time in nano seconds
        print('Function run time = {0:.4f} nano-seconds'.format(elapse_time))
        return
    return wrapper


@function_timer
def email_replace_1(infile):
    """This is the brute force method and not particular efficient on space complexity"""
    with open(infile, 'r') as f:
        f_out = f.read()   # read all the text at once as a string
        f.seek(0)  # Return the file counter to the beginning of the file

    email_regex = '[\w\.\-]+@[\w\.\-]+'
    email_list = re.findall(email_regex, f_out)  # find out how many emails are there in a file
    # print(f'email list = {email_list}')

    for email in email_list:
        nf_out = f_out.replace(email, 'name@abc.com')
        f_out = nf_out
    # print(nf_out)

    with open('test_email_output.txt', 'w') as nf:
        nf.write(nf_out)
    return


@function_timer
def email_replace_2(infile):
    """This is the to save space, limiting the string copy to the unmatched part of the string. This takes more time"""
    with open(infile, 'r') as f:
        f_out = f.read()   # read all the text at once as a string
        f.seek(0)  # Return the file counter to the beginning of the file

    email_regex = '[\w\.\-]+@[\w\.\-]+'
    nf_out = ''
    while True:
        # print(f'f_out = {f_out}')
        output = re.search(email_regex, f_out)
        if output is None:
            print('There is no email in the list')
            break
        # print(output.span())
        nf_out = nf_out + f_out[0:output.span()[0]] + 'name@abc.com'  # first ocurrence of the matched string position
        f_out = f_out[output.span()[1]:]
    # print(nf_out)

    with open('test_email_output.txt', 'w') as nf:
        nf.write(nf_out)
    return


def email_replace_3(infile):
    '''Use the regex substitute (re.sub) method to simplfy the code'''
    with open(infile, 'r') as f:
        f_out = f.read()   # read all the text at once as a string
    email_regex = '[\w\.\-]+@[\w\.\-]+'
    temp_str = re.sub(email_regex, 'name@abc.com', f_out)

    with open('test_email_output.txt', 'w') as nf:
        nf.write(temp_str)
    return


if __name__ == '__main__':
    _, filename = os.path.split('/usr/home/test/test_file.txt')  # will split the directory from the filename
    print(f'filename = {filename}')
    # email_replace_1('test_file.txt')
    # sleep(1)
    # email_replace_2('test_file.txt')
    email_replace_3('test_file.txt')
