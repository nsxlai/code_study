#!/usr/bin/env python3
"""
Medium source:
https://python.plainenglish.io/turn-your-python-script-into-a-real-program-with-docker-c200e15d5265

Python Virtual Environment (RealPython):
https://realpython.com/python-virtual-environments-a-primer/

Activating virtuaql environment in Docker:
https://pythonspeed.com/articles/activate-virtualenv-dockerfile/

Running docker on windows WSL2 (setup video):
https://nickjanetakis.com/blog/a-linux-dev-environment-on-windows-with-wsl-2-docker-desktop-and-more

Official Docker documentation for WSL
https://docs.docker.com/docker-for-windows/wsl/

Download Docker Desktop Utility
https://hub.docker.com/editions/community/docker-ce-desktop-windows/

"""
import logging
import os
import time
import sys
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler


# load variables from environemtn variables
verbose = int(os.environ.get('VERBOSE', 1))
directory = os.environ.get('DIRECTORY', os.path.join('top'))


if __name__ == '__main__':
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    event_handler = LoggingEventHandler()

    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
