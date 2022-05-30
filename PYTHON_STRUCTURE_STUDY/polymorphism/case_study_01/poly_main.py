"""
source: https://levelup.gitconnected.com/hidden-power-of-polymorphism-in-python-c9e2539c1633
code origin: https://github.com/pavel-fokin/py-polymorphism-study

Pros:
   1. they are testable, with a help of the unittest.mock library;
   2. they can follow encapsulation, with the usage of the imports you can hide details inside a module;
   3. you have Singleton pattern by default.

Cons:
   1. no inheritance_with_test for a modules, but it can be replaced with a composition in some cases.
"""
from PYTHON_STRUCTURE_STUDY.polymorphism import modules


def use_storage(storage):
    """Business case of storage usage."""

    storage.info()
    storage.add({"pk": 1, "data": "text"})
    storage.get(pk=1)


if __name__ == "__main__":
    s_list = [
        # Abstract Class Case
        PYTHON_STRUCTURE_STUDY.polymorphism.case_study_01.abstract.storages.Memory(),
        PYTHON_STRUCTURE_STUDY.polymorphism.case_study_01.abstract.storages.Persistent(),

        # Duck Typed Case
        PYTHON_STRUCTURE_STUDY.polymorphism.case_study_01.classes.storages.Memory(),
        PYTHON_STRUCTURE_STUDY.polymorphism.case_study_01.classes.storages.Persistent(),

        # Modules Case
        modules.storages.memory,
        modules.storages.persistent,
    ]

    for storage in s_list:
        use_storage(storage)
        print()
