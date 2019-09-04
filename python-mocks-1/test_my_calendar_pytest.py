# import unittest
from requests.exceptions import Timeout
import mock
import my_calendar
import pytest


mock_json = {'12/25': 'Christmas',
             '7/4': 'Independence Day'}


def log_request_success(url):
    # Log a fake request for test output purposes
    print(f'Making a request to {url}')
    print('Request received!')

    # Create a new Mock to imitate a Response
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = mock_json
    return response_mock


def log_request_page_not_found(url):
    # Log a fake request for test output purposes
    print(f'Making a request to {url}')
    print('Request received!')

    # Create a new Mock to imitate a Response
    response_mock = mock.MagicMock()
    response_mock.status_code = 404
    return response_mock


def log_request_bad_status_code(url):
    # Log a fake request for test output purposes
    print(f'Making a request to {url}')
    print('Request received!')

    # Create a new Mock to imitate a Response
    response_mock = mock.MagicMock()
    response_mock.status_code = 600
    return response_mock


@mock.patch.object(my_calendar.requests, 'get')
def test_get_holidays_with_success_status(mock_request_get):
    mock_request_get.side_effect = log_request_success
    result = my_calendar.get_holidays()
    # print(result)
    assert result['12/25'] == 'Christmas'


@mock.patch.object(my_calendar.requests, 'get')
def test_get_holidays_with_page_not_found(mock_request_get):
    mock_request_get.side_effect = log_request_page_not_found
    result = my_calendar.get_holidays()
    assert result == 'Page Not Found'


@mock.patch.object(my_calendar.requests, 'get')
def test_get_holidays_with_bad_status_code(mock_request_get):
    mock_request_get.side_effect = log_request_bad_status_code
    result = my_calendar.get_holidays()
    assert result is None


@mock.patch.object(my_calendar.requests, 'get')
def test_get_calendar_retry(mock_request_get):
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = mock_json

    # Set the side effect of .get()
    mock_request_get.side_effect = [Timeout, response_mock]

    # Test that the first request raises a Timeout
    with pytest.raises(Timeout):
        my_calendar.get_holidays()
        print('Raise Timeout exception')

    # Now retry, expecting a successful response
    assert my_calendar.get_holidays()['7/4'] == 'Independence Day'

    # Finally, assert .get() was called twice
    assert mock_request_get.call_count == 2


"""
# Mock requests to control its behavior
# requests = Mock()


class CalendarTest(unittest.TestCase):
    def log_request(self, url):
        # Log a fake request for test output purposes
        print(f'Making a request to {url}')
        print('Request received!')

        # Create a new Mock to imitate a Response
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            '12/25': 'Christmas',
            '7/4'  : 'Independence Day',
        }
        return response_mock

    def log_request_page_not_found(self, url):
        # Log a fake request for test output purposes
        print(f'Making a request to {url}')
        print('Request received!')

        # Create a new Mock to imitate a Response
        response_mock = Mock()
        response_mock.status_code = 404
        return response_mock

    def test_get_holidays_logging(self):
        # Test a connection timeout
        requests.get.side_effect = self.log_request
        assert get_holidays()['12/25'] == 'Christmas'

    def test_url_page_not_found(self):
        requests.get.side_effect = self.log_request_page_not_found
        assert get_holidays() == 'Page Not Found'

    def test_get_calendar_retry(self):
        response_mock = Mock()
        response_mock.status_code = 200
        response_mock.json.return_value = {
            '12/25': 'Christmas',
            '7/4'  : 'Independence Day',
        }
        # Set the side effect of .get()
        requests.get.side_effect = [Timeout, response_mock]

        # Test that the first request raises a Timeout
        with self.assertRaises(Timeout):
            get_holidays()

        # Now retry, expecting a successful response
        assert get_holidays()['12/25'] == 'Christmas'

        # Finally, assert .get() was called twice
        assert requests.get.call_count == 2
"""

"""
class CalendarTests(unittest.TestCase):
    @patch('my_calendar.requests')
    def test_get_holidays_timeout(self, mock_requests):
        mock_requests.get.side_effect = Timeout
        with self.assertRaises(Timeout):
            get_holidays()
            mock_requests.get_assert_called_once()


class CalendarTests_p2(unittest.TestCase):
    @patch.object(requests, 'get', side_effect=requests.exceptions.Timeout)
    def test_get_holidays_timeout(self, mock_requests):
        with self.assertRaises(requests.exceptions.Timeout):
            get_holidays()
"""