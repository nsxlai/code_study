"""
https://docs.python.org/3/howto/logging-cookbook.html (edited)
"""
import logging
import sys


LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s]::%(module)s::%(lineno)d::%(levelname)s:: %(message)s"


def get_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)  # Needs to be lowest level to allow handlers to filter later
    return log


def setup_logging(stream_level=LOG_LEVEL, file_path=None):
    """Setup basic logging.

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

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(stream_level)
    sh.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.root.addHandler(sh)

    if file_path is not None:
        fh = logging.FileHandler(file_path)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(LOG_FORMAT))
        logging.root.addHandler(fh)


