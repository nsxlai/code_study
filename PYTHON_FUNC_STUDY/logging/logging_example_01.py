"""
source: https://majianglin2003.medium.com/python-logging-6a688fa63587
github: https://gist.github.com/nguyenkims/e92df0f8bd49973f0c94bddf36ed7fd0
"""
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from time import sleep


FORMATTER = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
LOG_FILE = "logging_example_01.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.INFO) # better to have too much log than not enough

    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())

    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False

    return logger


if __name__ == '__main__':
    logger = get_logger('logging_example')
    logger.info('Logging starting...')
    sleep(2)
    logger.info('Executing...')
    sleep(2)
    logger.info('Test 1 running...')
    sleep(2)
    logger.info('Test 1 completed...')
