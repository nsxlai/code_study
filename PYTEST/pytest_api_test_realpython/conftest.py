import mock
from PYTEST import fixture


@fixture(scope='function')
def print_message():
    return 'Debug message'
