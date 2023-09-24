"""
This example is based on the async_medium_example.py
"""
import asyncio
import numpy as np
import logging
import sys
from time import sleep


LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s]::%(module)s::%(lineno)d::%(levelname)s:: %(message)s"


def create_logger(name: str, root_level=True):
    """
    use logging handler to handle multiple logging destination (STDOUT and file)

    Borrow the code from logging_example_05.py

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
    Logger.info('creating the logger...')

    stream_handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(LOG_FORMAT)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    Logger.setLevel(LOG_LEVEL)  # Logger.setLevel set the base level; stream_handler will overwrite the level
    Logger.addHandler(stream_handler)

    return Logger


async def num_gen_1():
    """
    Generate random number every 1 second
    """
    n = int(np.random.random() * 100)
    await asyncio.sleep(1)
    logger.info(f'Running num_gen1: {n}')
    return n


async def num_gen_2():
    """
    Generate random number every 2 second
    """
    n = int(np.random.random() * 100)
    await asyncio.sleep(2)
    logger.info(f'Running num_gen2: {n}')
    return n


async def num_gen_3():
    """
    Generate random number every 3 second
    """
    n = int(np.random.random() * 100)
    await asyncio.sleep(3)
    logger.info(f'Running num_gen3: {n}')
    return n


async def main():

    p1 = num_gen_1()
    p2 = num_gen_2()
    p3 = num_gen_1()
    p4 = num_gen_3()
    p5 = num_gen_2()
    p6 = num_gen_1()
    p7 = num_gen_3()

    coro_objs = [p1, p2, p3, p4, p5, p6, p7gg]

    logger.info('Setting up coroutines...')
    await asyncio.gather(*coro_objs)
    logger.info('Finish coroutines...')


if __name__ == '__main__':

    logger = create_logger(__name__)
    asyncio.run(main())
