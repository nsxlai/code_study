from unittest import mock
from mock import Mock
from mock import patch
from mock import MagicMock
import pytest_mock_generator as mg


# from .process_and_zip import Process_and_Zip
from PYTEST.pytest_medium_example import process_and_zip

# mocked dependencies
mock_ZipFile = MagicMock(name='ZipFile')
mock.patch('PYTEST.pytest_medium_example.zipfile.ZipFile', new=mock_ZipFile)
# calls to generate_asserts, put this after the 'act'
mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')


@patch.object(process_and_zip, 'Process_and_Zip')
def test_process_and_zip():
        # arrange: todo
        mg.generate_uut_mocks_with_asserts(process_and_zip)

        # act: invoking the tested code
        process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')

        # assert: todo



----------------
from tests.sample.code.tested_module import process_and_zip


def test_process_and_zip(mocker, mg):
    # arrange: todo
    mg.generate_uut_mocks_with_asserts(process_and_zip)

    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')

    # assert: todo


# mocked dependencies
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
# calls to generate_asserts, put this after the 'act'
mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')

\

from tests.sample.code.tested_module import process_and_zip


def test_process_and_zip(mocker, mg):
    # arrange:
    # mocked dependencies
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)

    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')

    # assert: todo
    # calls to generate_asserts, put this after the 'act'
    mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')


assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)




def test_process_and_zip(mocker):
    # arrange:
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)

    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')

    # assert:
    mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
    mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')

