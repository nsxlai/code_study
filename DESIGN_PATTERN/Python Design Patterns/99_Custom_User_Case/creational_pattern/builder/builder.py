"""
source: https://python.plainenglish.io/design-patterns-in-python-builder-pattern-d921fbac7fb3
"""
from abc import ABC, abstractmethod


# PRODUCT
class Drum:

    def __init__(self):
        self.__snare = None
        self.__hihat = None
        self.__bass = None

    def set_snare(self, snare):
        self.__snare = snare

    def set_hihat(self, hihat):
        self.__hihat = hihat

    def set_bass(self, bass):
        self.__bass = bass

    def product_properties(self):
        print(f"Snare: {self.__snare.inch}, Hihat: {self.__hihat.brand}, Bass: {self.__bass.leather}")


# COMPONENTS OF THE PRODUCT
class Snare:
    inch = None


class Hihat:
    brand = None


class Bass:
    leather = None


# BUILDER INTERFACE
class IBuilder(ABC):

    @abstractmethod
    def get_snare(self):
        "assembly snare"

    @abstractmethod
    def get_hihat(self):
        "assembly hihat"

    @abstractmethod
    def get_bass(self):
        "assembly bass"


# CONCRETE BUILDERS
class JazzyBuilder(IBuilder):

    def get_snare(self):
        snare = Snare()
        snare.inch = 15
        return snare

    def get_hihat(self):
        hihat = Hihat()
        hihat.brand = "İstanbul"
        return hihat

    def get_bass(self):
        bass = Bass()
        bass.leather = "Soft"
        return bass


class MetalBuilder(IBuilder):

    def get_snare(self):
        snare = Snare()
        snare.inch = 14
        return snare

    def get_hihat(self):
        hihat = Hihat()
        hihat.brand = "Zildjian"
        return hihat

    def get_bass(self):
        bass = Bass()
        bass.leather = "Hard"
        return bass


# DIRECTOR
class Director:
    __builder = None

    def set_builder(self, builder):
        self.__builder = builder

    def get_drum(self):
        drum = Drum()

        snare = self.__builder.get_snare()
        drum.set_snare(snare)

        hihat = self.__builder.get_hihat()
        drum.set_hihat(hihat)

        bass = self.__builder.get_bass()
        drum.set_bass(bass)

        return drum


if __name__ == '__main__':
    jazz_builder = JazzyBuilder()
    metal_builder = MetalBuilder()

    director = Director()
    director.set_builder(jazz_builder)
    jazz_drum = director.get_drum()
    jazz_drum.product_properties()

    director.set_builder(metal_builder)
    metal_drum = director.get_drum()
    metal_drum.product_properties()
