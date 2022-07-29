"""
source: https://www.delftstack.com/howto/python/python-logging-stdout/
"""
import logging
import sys
import time


LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s]::%(name)s::%(lineno)d::%(levelname)s::%(message)s"
LOG_FILE = 'logging_example_05.log'


def create_logger(name, root_level=True):
    """
    use logging handler to handle multiple logging destination (STDOUT and file)
    """

    if root_level:
        name = "logging_example." + name

    Logger = logging.getLogger(name)
    Logger.info('createing the logger...')

    file_handler = logging.FileHandler(LOG_FILE)
    stream_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    Logger.addHandler(stream_handler)
    Logger.addHandler(file_handler)

    return Logger


if __name__ == '__main__':
    logger = create_logger(__name__)
    logger.info('Initial log...')
    time.sleep(2)
    logger.info('Progress point #1...')
    time.sleep(1)
    logger.warning('Possible issue here...')
    time.sleep(1)
    logger.info('Progress point #2...')
    time.sleep(1)
    logger.error('Encounter error...')

