"""
Design a retry test function that will exectue the test 3 times.
If the 4th try still fails, fail the overall test
"""
import time
import random


def sys_test():
    print('System test...')
    random.choice(['Pass', 'Fail'])


def retry_feature():
    # insert code here
    sys_test()
    # insert code here
