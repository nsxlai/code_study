"""
source: https://medium.com/geekculture/chain-of-responsibility-pattern-in-python-9662680b8567

Chain structure:
  Logger -> DebugHandler (10) -> InfoHandler (20) -> WarningHandler (30) -> ErrorHandler (40) -> FailureHandler (50)

For this example:
  Logger -> InfoHandler (10) -> ErrorHandler (40) -> FailureHandler (50)
"""
from abc import ABC, abstractmethod


class IHandler(ABC):
    @abstractmethod
    def handle(self, message):
        pass


class DebugHandler(IHandler):
    def __init__(self, _next: IHandler):
        self._next = _next

    def handle(self, message):
        if message.startswith("debug"):
            print("DEBUG (10)", message)
        else:
            self._next.handle(message)


class InfoHandler(IHandler):
    def __init__(self, _next: IHandler):
        self._next = _next

    def handle(self, message):
        if message.startswith("info"):
            print("INFO (20)", message)
        else:
            self._next.handle(message)


class WarningHandler(IHandler):
    def __init__(self, _next: IHandler):
        self._next = _next

    def handle(self, message):
        if message.startswith("warning"):
            print("WARNING (30)", message)
        else:
            self._next.handle(message)


class ErrorHandler(IHandler):
    def __init__(self, _next: IHandler):
        self._next = _next

    def handle(self, message):
        if message.startswith("error"):
            print("ERROR (40)", message)
        else:
            self._next.handle(message)


class FailureHandler(IHandler):
    def __init__(self, _next: IHandler):
        self._next = _next

    def handle(self, message):
        if message.startswith("failure"):
            print("FAILURE (50)", message)
        else:
            self._next.handle(message)


class NullHandler(IHandler):
    def __init__(self):
        pass

    def handle(self, message: str):
        print("Message mute")


class Logger:
    def __init__(self):
        nullHandler = NullHandler()
        self.failureHandler = FailureHandler(nullHandler)
        self.errorHandler = ErrorHandler(self.failureHandler)
        self.infoHandler = InfoHandler(self.errorHandler)
        self.handler = None

    def log(self, message: str):
        self.handler.handle(message)

    def set_handler(self, handler: str):
        if handler.lower() == 'info':
            self.handler = self.infoHandler
        elif handler.lower() == 'error':
            self.handler = self.errorHandler
        elif handler.lower() == 'failure':
            self.handler = self.failureHandler


if __name__ == '__main__':
    logger = Logger()

    print('Set logger level to INFO...')
    logger.set_handler('info')
    logger.log("failure - message 1")
    logger.log("info - message 2")
    logger.log("error - message 3")

    print('\nSet logger level to ERROR...')
    logger.set_handler('error')
    logger.log("failure - message 1")
    logger.log("info - message 2")
    logger.log("error - message 3")

    print('\nSet logger level to FAILURE...')
    logger.set_handler('failure')
    logger.log("failure - message 1")
    logger.log("info - message 2")
    logger.log("error - message 3")
