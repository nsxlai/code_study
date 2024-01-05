"""
source: https://medium.com/@amirm.lavasani/design-patterns-in-python-factory-method-1882d9a06cb4

See both abstract_factory_03.py and factory_03.py for pattern comparison.

Factory Method Pattern: Creates a single product using subclasses with a method for each product.
                        Focuses on individual product creation.
Abstract Factory Pattern: Creates entire families of related products with consistent interfaces.
                          Emphasizes creating multiple related objects.
"""
from abc import ABC, abstractmethod


# Step 1: Defining the Product
class Localizer(ABC):
    """Abstract Product: Represents translations for specific languages."""
    @abstractmethod
    def localize(self, msg: str):
        """Translate the given message."""
        pass


# Step 2: Creating Concrete Products
class FrenchLocalizer(Localizer):
    """Concrete Product: Represents translations for French."""
    def __init__(self):
        self.translations = {
          'car': 'voiture',
          'bike': 'bicyclette',
          'cycle': 'cyclette',
        }

    def localize(self, msg: str) -> str:
        """Translate the message to French."""
        return self.translations.get(msg, msg)


class SpanishLocalizer(Localizer):
    """Concrete Product: Represents translations for Spanish."""
    def __init__(self):
        self.translations = {
          'car': 'coche',
          'bike': 'bicicleta',
          'cycle': 'ciclo',
        }

    def localize(self, msg: str) -> str:
        """Translate the message to Spanish."""
        return self.translations.get(msg, msg)


class EnglishLocalizer(Localizer):
    """Concrete Product: Represents translations for English."""
    def localize(self, msg: str) -> str:
        """Return the message as is (no translation)."""
        return msg


# Step 3: Defining the Creator
class LocalizerFactory(ABC):
    """Abstract Creator: Defines the Factory Method to create localizers."""
    @abstractmethod
    def create_localizer(self):
        """Factory Method: Create a Localizer instance."""
        pass


# Step 4: Implementing Concrete Creators
class FrenchLocalizerFactory(LocalizerFactory):
    """Concrete Creator: Creates FrenchLocalizer instances."""
    def create_localizer(self):
        """Factory Method implementation for creating FrenchLocalizer."""
        return FrenchLocalizer()


class SpanishLocalizerFactory(LocalizerFactory):
    """Concrete Creator: Creates SpanishLocalizer instances."""
    def create_localizer(self):
        """Factory Method implementation for creating SpanishLocalizer."""
        return SpanishLocalizer()


class EnglishLocalizerFactory(LocalizerFactory):
    """Concrete Creator: Creates EnglishLocalizer instances."""
    def create_localizer(self):
        """Factory Method implementation for creating EnglishLocalizer."""
        return EnglishLocalizer()


# Step 5: Utilizing the Factory
def create_localizer(language="English"):
    """
    Factory Method: Create a localizer for the specified language.

    Args:
        language (str): The language for which to create a localizer.

    Returns:
        Localizer: An instance of the localizer for the specified language.
    """
    localizers = {
        "French": FrenchLocalizer,
        "English": EnglishLocalizer,
        "Spanish": SpanishLocalizer,
    }
    return localizers[language]()


if __name__ == "__main__":
    # Create localizers for different languages
    french_localizer = create_localizer("French")
    english_localizer = create_localizer("English")
    spanish_localizer = create_localizer("Spanish")

    message = ["car", "bike", "cycle"]

    for msg in message:
        # Print localized messages for each language
        print(french_localizer.localize(msg))
        print(english_localizer.localize(msg))
        print(spanish_localizer.localize(msg))
