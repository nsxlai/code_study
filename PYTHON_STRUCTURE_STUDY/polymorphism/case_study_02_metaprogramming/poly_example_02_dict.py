"""
source: https://medium.com/@angusyuen/writing-maintainable-pythonic-code-metaprogramming-with-decorators-2fc2f1d358db
"""
from abc import ABC, abstractmethod


class FileHandler(ABC):
    @abstractmethod
    def write(self, path):
        raise NotImplementedError


class CSVHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as CSV
        print(f"Successfully wrote {data} to CSV!")


class JSONHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as JSON
        print(f"Successfully wrote {data} to JSON!")


class TXTHandler(FileHandler):
    def write(self, data):
        # Some implementation to write data out as TXT
        print(f"Successfully wrote {data} to TXT!")


class HandlerFactory:
    """
    This implementation uses the internally stored dict structure to keep track of the factory methods
    """
    file_handlers = {
        "csv": CSVHandler,
        "json": JSONHandler,
        "txt": TXTHandler,
    }

    def get_handler(self, output_type):
        handler = self.file_handlers.get(output_type)
        if handler is None:
            raise ValueError('No such file type supported!!')
        return handler()


if __name__ == '__main__':
    output_type = ['csv', 'txt', 'json', 'h5']

    for t in output_type:
        handler = HandlerFactory().get_handler(t)
        handler.write("dummy-data")
