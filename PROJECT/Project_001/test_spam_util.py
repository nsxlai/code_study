import spam_util
import config
import mock
from pytest import mark, raises
from mock import patch
import json

solenoid_output_success = {'api': '/api/v1.0/spam/solenoid/set', 'status': 'success'}
solenoid_output_failed = {'api': '/api/v1.0/spam/solenoid/set', 'status': 'failed'}


# @mock.object(spam_util.requests, 'post')
# @mark.parametrize('s_state, s_bank', [('on', 0), ('off', 0), ('on', 1), ('off', 1)])
# def test_solenoid(s_state, s_bank, mock_request_post):
#     mock_request_post = solenoid_output
#     spam_util.solenoid(s_state, s_bank)


def solenoid_response_success(url):
    print(f'Making request to {url}')
    response_mock = mock.MagicMock()
    response_mock.status_code = 200
    response_mock.return_value = solenoid_output_success
    return response_mock


def solenoid_response_failed(url):
    print(f'Making request to {url}')
    response_mock = mock.MagicMock()
    response_mock.status_code = 404
    response_mock.return_value = solenoid_output_failed
    return response_mock


solenoid_on = [(config.spam_dut.get('solenoid_on'), 0, False),
               (config.spam_dut.get('solenoid_on'), 1, False),
               (config.spam_dut.get('solenoid_on'), 2, False),
               (config.spam_dut.get('solenoid_on'), 3, False),
               (config.spam_dut.get('solenoid_on'), 4, False),
               (config.spam_dut.get('solenoid_on'), 5, False),
               (config.spam_dut.get('solenoid_on'), 6, False),
               (config.spam_dut.get('solenoid_on'), 7, False)]

solenoid_off = [(config.spam_dut.get('solenoid_off'), 0, False),
                (config.spam_dut.get('solenoid_off'), 1, False),
                (config.spam_dut.get('solenoid_off'), 2, False),
                (config.spam_dut.get('solenoid_off'), 3, False),
                (config.spam_dut.get('solenoid_off'), 4, False),
                (config.spam_dut.get('solenoid_off'), 5, False),
                (config.spam_dut.get('solenoid_off'), 6, False),
                (config.spam_dut.get('solenoid_off'), 7, False)]

solenoid = solenoid_on + solenoid_off


@mark.parametrize('feature_type, port, verbose', solenoid)
@mock.patch.object(spam_util.requests, 'post')
def test_feature_solenoid_success_cases(mock_requests_post, feature_type, port, verbose):
    mock_requests_post.side_effect = solenoid_response_success
    result = spam_util.feature(feature_type, port, verbose)
    assert result is False


@mark.parametrize('feature_type, port, verbose', solenoid)
@mock.patch.object(spam_util.requests, 'post')
def test_feature_solenoid_failed_cases(mock_requests_post, feature_type, port, verbose):
    mock_requests_post.side_effect = solenoid_response_failed
    result = spam_util.feature(feature_type, port, verbose)
    assert result is True
