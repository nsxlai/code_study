from unittest import mock
from mock import Mock
from mock import patch
from mock import MagicMock
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
