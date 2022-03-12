 """
source: https://medium.com/pythoneers/master-logging-in-python-73cd2ff4a7cb

The Five Levels of Logging
DEBUG: It is used for diagnosing the problem. It gives a piece of detailed information about the problem.
       The severity level is 10.
INFO: It gives the confirmation message of the successful execution of the program.
      The severity level is 20.
WARNING: The message is for when an unexpected situation occurs.
         The severity level is 30.
ERROR: It is due to a more serious problem than a warning. It can be due to some inbuilt error Like
       syntax or logical error.
       The severity level is 40.
CRITICAL: It occurs when the program execution stops and it can not run itself anymore.
          The severity level is 50.

We can Print the DEBUG and INFO message too by changing the basic configuration of the logger with
the help of basicConfig(**kwargs)
There are some parameters that are commonly used in this —
level: To change the root logger to a specified severity level.
filename: Filename where the logs going to be stored.
filemode: If a filename is given then this specifies the file mode in which the file will open. default is append (a )
format: This is the format of the log message.
datefmt : It specified the date and time format.
"""
import time
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from logging.handlers import TimedRotatingFileHandler


LOG_FILENAME = 'logging_example_03.log'


def logger_exp_01():
    """ Simple logger example """
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')


def logger_exp_02():
    """ Simple logging example; adding basic config and formatting """
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S')
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')


def logger_exp_03():
    """ Intermediary logging example; also logging to a file """
    logging.basicConfig(level=logging.DEBUG, filename=LOG_FILENAME, filemode='a',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    name = str(input("Enter Your Name: "))
    logging.info(f"{name} has logged in successfully !!")
    logging.debug('Just a debug message; no significant output...')
    logging.warning('Reactor core temperature is reaching critical...')
    logging.critical('Reactor core temperature is at critical...')
    logging.error('Reactor failure!! Unable to stabilize control!!')

    # Logging the error without raise the exception_with_test and exit the program
    a = 10
    b = 0
    try:
        c = a / b
    except ZeroDivisionError as e:
        logging.error("Exception Occurred", exc_info=True)  ## At default it is True


def logger_exp_04():
    """
    Suppose You have an application and You want to take logs of the application.
    You want to save logs higher than the WARNING severity level to a log file and Higher than INFO on the console.
    """
    # create different types of logging handler to handle different type of logging output
    logger = logging.getLogger(__name__)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(LOG_FILENAME)
    c_handler.setLevel(logging.WARNING)  # Will log anything higher than WARNING to console (including WARNING level)
    f_handler.setLevel(logging.WARNING)  # Will log anything higher than ERROR to file (including ERROR level)
    # For some reason, the WARNING and above (WARNING, ERROR, and CRITICAL) will be logged. The INFO and DEBUG are not
    # logged in both handler

    # Create formatters and add it to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    logger.debug('1/10 - This is DEBUG')
    logger.info('2/10 - This is INFO')
    logger.warning('3/10 - This is WARNING')
    logger.error('4/10 - This is ERROR')
    logger.critical('5/10 - This is CRITICAL')
    logger.warning('6/10 - This is WARNING')
    logger.info('7/10 - This is INFO')
    logger.info('8/10 - This is INFO')
    logger.critical('9/10 - This is CRITICAL')
    logger.debug('10/10 - This is DEBUG')

    logging.debug('DEBUG - Outside of logger')


def logger_exp_05():
    """
    Use a config file to specific the logging configuration
    """
    # Loads The Config File
    logging.config.fileConfig('logging_example_03.conf')

    # create a logger with the name from the config file.
    # This logger now has StreamHandler with DEBUG Level and the specified format in the logging.conf file
    logger = logging.getLogger('simpleExample')

    # Log Messages
    logging.debug('This is a debug message')
    logging.info('This is an info message')
    logging.warning('This is a warning message')
    logging.error('This is an error message')
    logging.critical('This is a critical message')


def logger_exp_06():
    """
    When You are working with a large application and you have so many events to log and you only
    need to keep track of the most recent events then you should use a rotating file handler.
    It helps you to set a byte limit for your file and if the limit reaches then all the previous
    logs replaced by new logs. You can even create multiple backups of the file.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    # roll over after 2KB, and keep backup logs app.log.1, app.log.2 , etc.
    handler = RotatingFileHandler('app.log', maxBytes=2000, backupCount=5)
    logger.addHandler(handler)

    for i in range(5000):
        logger.info(i)


def logger_exp_07():
    """
    If Your application is running for a long amount of time then you can use TimedRotatingFileHandle.
    It will create a new log file in the specified time limit and then overwrite the old files.
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a log file every seconds with a new log detail at the inteval of 2
    handler = TimedRotatingFileHandler('app.log', when='s', interval=2, backupCount=3)
    logger.addHandler(handler)

    for i in range(20):
        logger.info(i)
        time.sleep(2)


if __name__ == '__main__':
    # logger_exp_01()
    # logger_exp_02()
    # logger_exp_03()
    # logger_exp_04()
    # logger_exp_05()
    logger_exp_06()
