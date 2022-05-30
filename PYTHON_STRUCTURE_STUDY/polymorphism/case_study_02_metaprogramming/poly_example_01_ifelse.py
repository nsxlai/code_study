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
    This is not great because of the following reasons:
        1. Every time we support a new file type, we have to modify the Factory if / else creation logic
        2. Does not comply with Open - Closed Principle, “software entities should be open for extension,
           but closed for modification”
    """
    @staticmethod
    def get_handler(output_type):
        if output_type == "csv":
            return CSVHandler()

        elif output_type == "json":
            return JSONHandler()

        elif output_type == "txt":
            return TXTHandler()


if __name__ == '__main__':
    output_type = ['csv', 'txt', 'json']

    for t in output_type:
        handler = HandlerFactory().get_handler(t)
        handler.write("dummy-data")
