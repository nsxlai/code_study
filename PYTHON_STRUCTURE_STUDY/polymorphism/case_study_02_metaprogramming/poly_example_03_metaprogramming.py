"""
source: https://medium.com/@angusyuen/writing-maintainable-pythonic-code-metaprogramming-with-decorators-2fc2f1d358db
"""
from abc import ABC, abstractmethod


class HandlerFactory:
    """
    The file handler will be use metaprogramming technique, which means the dictionary will auto-populate at
    run time due to the decorator.
    """
    file_handlers = {}

    @classmethod
    def register_handler(cls, output_type):
        def wrapper(handler_cls):
            cls.file_handlers[output_type] = handler_cls
            return handler_cls
        return wrapper

    @classmethod
    def get_handler(cls, output_type):
        handler = cls.file_handlers.get(output_type)
        if handler is None:
            raise ValueError('No such file type supported!!')
        return handler()


class FileHandler(ABC):
    @abstractmethod
    def write(self, path):
        raise NotImplementedError


# Any classes with this decorator will automatically
# register itself with the Factory dict
@HandlerFactory.register_handler("csv")
class CSVHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as CSV
        print(f"Successfully wrote {data} to CSV!")


@HandlerFactory.register_handler("json")
class JSONHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as JSON
        print(f"Successfully wrote {data} to JSON!")


@HandlerFactory.register_handler("txt")
class TXTHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as TXT
        print(f"Successfully wrote {data} to TXT!")


@HandlerFactory.register_handler("h5")
class TXTHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as H5
        print(f"Successfully wrote {data} to H5!")


if __name__ == '__main__':
    output_type = ['csv', 'txt', 'json', 'h5']

    for t in output_type:
        handler = HandlerFactory().get_handler(t)
        handler.write("dummy-data")
