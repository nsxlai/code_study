import mock
from pytest import fixture


@fixture(scope='function')
def print_message():
    return 'Debug message'
