from PROJECT.Project_001 import spam_util
from PROJECT.Project_001 import config
import mock
from pytest import mark, raises
from mock import patch

solenoid_output = {'api': '/api/v1.0/spam/solenoid/set', 'status': 'success'}


# @mock.object(spam_util.requests, 'post')
# @mark.parametrize('s_state, s_bank', [('on', 0), ('off', 0), ('on', 1), ('off', 1)])
# def test_solenoid(s_state, s_bank, mock_request_post):
#     mock_request_post = solenoid_output
#     spam_util.solenoid(s_state, s_bank)


def solenoid_response_success(url):
    print(f'Making request to {url}')
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.return_value = solenoid_output
    return response_mock


@mock.patch.object(spam_util.requests, 'post')
def test_feature(mock_requests_post):
    mock_requests_post.side_effect = solenoid_response_success
    result = spam_util.feature(config.spam_dut.get('solenoid_on'), 0, False)
    assert result is False
