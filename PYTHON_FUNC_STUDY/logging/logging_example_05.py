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

    Parameters
    ----------
    loglevel : int
        Minimum loglevel for emitting messages.
        CRITICAL = 50
        ERROR = 40
        WARNING = 30
        INFO = 20
        DEBUG = 10
        NOTSET = 0
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
    file_handler.setLevel(logging.WARNING)

    Logger.setLevel(LOG_LEVEL)  # Logger.setLevel does not overwrite file_handler.setLevel
    Logger.addHandler(stream_handler)
    Logger.addHandler(file_handler)

    return Logger


if __name__ == '__main__':
    """
    Logger.setLevel: not set
    |--> stream_handler.setLevel(logging.INFO)
    |--> file_handler.setLevel(logging.WARNING)

    If the Logger.setLevel is not set and the children handlers will use the higher handler level of the 2.
    In this case logging.WARNING level will be use and overwriting the logging.INFO


    Logger.setLevel(logging.INFO)
    |--> stream_handler.setLevel(logging.CRITICAL)
    |--> file_handler.setLevel(logging.WARNING)
    
    If the Logger.setLevel is set, this will ensure both handler will be at least at the Logger.setLevel. The
    children handler can set to higher level for customization 
    """
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
    time.sleep(1)
    logger.critical('Troubleshoot here...')

