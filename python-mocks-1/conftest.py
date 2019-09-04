import mock
from pytest import fixture


@fixture(scope='session')
def log_request_success(url):
    # Log a fake request for test output purposes
    print(f'Making a request to {url}')
    print('Request received!')

    # Create a new Mock to imitate a Response
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = mock_json
    return response_mock