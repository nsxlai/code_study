# source: realpython.com/python-interface


class InformalParserInterface:
    def load_data_source(self, path: str, file_name: str) -> str:
        """Load in the file for extracting test"""
        pass

    def extract_text(self, full_file_name: str) -> dict:
        """Extract test from the currently loaded file"""
        pass


class PdfParser(InformalParserInterface):
    """Extract text from a PDF"""
    def load_data_source(self, path: str, file_name: str) -> str:
        """Override InformalParserInterface.load_data_source()"""
        pass

    def extract_text(self, full_file_path: str) -> dict:
        """Override InformalParserInterface.extract_text()"""
        pass


class EmlParser(InformalParserInterface):
    """Extract text from an email"""
    def load_data_source(self, path: str, file_name: str) -> str:
        """Override InformalParserInterface.load_data_source()"""
        pass

    def extract_text_from_email(self, full_file_path: str) -> dict:
        """Do not override InformalParserInterface.extract_text()"""
        pass


class ParserMeta(type):
    """A Parser metaclass that will be used for parser class creation"""
    def __instancecheck__(cls, instance):
        return cls.__subclasscheck__(type(instance))

    def __subclasscheck__(cls, subclass):
        return (hasattr(subclass, 'load_data_source') and
                callable(subclass.load_data_source) and
                hasattr(subclass, 'extract_text') and
                callable(subclass.extract_text))


class UpdatedInformalParserInterface(metaclass=ParserMeta):
    """This interface is used for concrete classes to inherit from. There
       is no need to define the ParserMeta methods as any class as they are
       implicitly made available via .__subclasscheck__()
    """
    pass


class PdfParserNew:
    """Extract text from PDF"""
    def load_data_source(self, path: str, file_name: str) -> str:
        """Override InformalParserInterface.load_data_source()"""
        pass

    def extract_text(self, full_file_path: str) -> dict:
        """Override InformalParserInterface.extract_text()"""
        pass


class EmlParserNew:
    """Extract text from an email"""
    def load_data_source(self, path: str, file_name: str) -> str:
        """Override InformalParserInterface.load_data_source()"""
        pass

    def extract_text_from_email(self, full_file_path: str) -> dict:
        """Do not override InformalParserInterface.extract_text()"""
        pass


if __name__ == '__main__':
    print(issubclass(PdfParser, InformalParserInterface))
    print(issubclass(EmlParser, InformalParserInterface))
    print(PdfParser.__mro__)
    print(EmlParser.__mro__)
    print('Both of the subclass ended up to belong to the InformalParserInterface even though EmlParser does not')
    print('have the proper concrete implementation of the InformalParserInterface')
    print()
    print(issubclass(PdfParserNew, UpdatedInformalParserInterface))
    print(issubclass(EmlParserNew, UpdatedInformalParserInterface))
    print(PdfParserNew.__mro__)
    print(EmlParserNew.__mro__)
