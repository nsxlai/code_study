import sys
from io import StringIO
import pytest
from unittest import mock
import builtins
from PYTEST.argparse_pytest import example_main
from mock import patch


@pytest.mark.parametrize("from_user, response, output", [
    (['x', 'x', 'No'], False, "Please respond with 'y' or 'n'\n" * 2),
    ('y', True, ''),
    ('n', False, ''),
    (['x', 'y'], True, "Please respond with 'y' or 'n'\n"),
])
def test_get_from_user(from_user, response, output):
    from_user = list(from_user) if isinstance(from_user, list) \
        else [from_user]
    with mock.patch.object(builtins, 'input', lambda x: from_user.pop(0)):
        with mock.patch('sys.stdout', new_callable=StringIO):
            assert response == example_main.confirm()
            assert output == sys.stdout.getvalue()


@pytest.mark.parametrize("argv, called, response", [
    ([], False, None),
    (['-d'], True, False),
    (['-d'], True, True),
])
def test_get_from_user(argv, called, response):
    # global example_main.confirm
    original_confirm = example_main.confirm
    confirm = mock.Mock(return_value=response)
    with mock.patch('sys.argv', [''] + argv):
        if called and not response:
            with pytest.raises(SystemExit):
                example_main.main()
        else:
            example_main.main()

        assert confirm.called == called
    example_main.confirm = original_confirm


@pytest.mark.parametrize("argv, called, response", [
    ([], False, None),
    (['-d'], True, False),
    (['-d'], True, True),
])
@patch.object(example_main, 'confirm')
def test_get_from_user_method_2(mock_confirm, argv, called, response):
    confirm = mock.Mock(return_value=response)
    with mock.patch('sys.argv', [''] + argv):
        if called and not response:
            with pytest.raises(SystemExit):
                example_main.main()
        else:
            example_main.main()

        assert confirm.called == called


pytest.main('-x test_example_main.py'.split())
