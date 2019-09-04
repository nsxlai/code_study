import unittest
from my_calendar import get_holidays
from my calendar import requests
from requests.exceptions import Timeout
from unittest.mock import Mock
from unittest.mock import patch

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


if __name__ == '__main__':
    unittest.main()