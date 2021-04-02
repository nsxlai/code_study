from . import spam_util
import mock
from pytest import mark, raises
from mock import patch


def test_solenoid():
    assert spam_util.solenoid(s_state='on', s_bank=0) == None
