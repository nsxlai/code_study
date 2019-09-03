import mock

from .. import ut_sequence
from apollo.libs import lib

PASS = 'anything we want'
FAIL = 'anything else we want?'
SERIAL_NUMBER = 'SN'
UUT_TYPE = 'pid'
AREA = 'prev_area'
CLOSED = 'closed'
OPENED = 'opened'


def test_ut_sequence_definition():
    seq = ut_sequence.ut_sequence_definition()
    assert ['areacheck', 'run_tests'] == seq.step_names


@mock.patch.object(ut_sequence.lib, 'apdicts')
@mock.patch.object(ut_sequence.lib, 'PASS', PASS)
@mock.patch.object(ut_sequence.cesiumlib, 'verify_area')
def test_areacheck(mock_verify_area, mock_apdicts):
    mock_apdicts.userdict = dict()
    mock_apdicts.userdict['serial_number'] = SERIAL_NUMBER
    mock_apdicts.userdict['uut_type'] = UUT_TYPE
    assert PASS == ut_sequence.areacheck(AREA)
    mock_verify_area.assert_called_with(serial_number=SERIAL_NUMBER,
                                        uut_type=UUT_TYPE,
                                        area=AREA)


@mock.patch.object(ut_sequence.lib, 'apdicts')
@mock.patch.object(ut_sequence.lib, 'FAIL', FAIL)
@mock.patch.object(ut_sequence.cesiumlib, 'verify_area')
def test_areacheck_failure(mock_verify_area, mock_apdicts):
    mock_apdicts.userdict = dict()
    mock_apdicts.userdict['serial_number'] = SERIAL_NUMBER
    mock_apdicts.userdict['uut_type'] = UUT_TYPE
    mock_verify_area.side_effect = Exception()
    assert (FAIL, 'Failed areacheck.') == ut_sequence.areacheck(AREA)
    mock_verify_area.assert_called_with(serial_number=SERIAL_NUMBER,
                                        uut_type=UUT_TYPE,
                                        area=AREA)


@mock.patch.object(ut_sequence.lib, 'conn')
def test_run_tests(mock_conn):
    send_dict = {'run test1\n': 'passed\n#'}
    mock_conn.uut = FakeConn(send_dict)
    assert lib.PASS == ut_sequence.run_tests()
    assert CLOSED == mock_conn.uut.status


@mock.patch.object(ut_sequence.lib, 'conn')
def test_run_tests_failed(mock_conn):
    send_dict = {'run test1\n': 'failed\n#'}
    mock_conn.uut = FakeConn(send_dict)
    assert (lib.FAIL, 'test1 failed') == ut_sequence.run_tests()
    assert CLOSED == mock_conn.uut.status


class FakeConn:
    def __init__(self, send_dict):
        self.recbuf = ''
        self.send_dict = send_dict
        self.status = CLOSED

    def open(self):
        self.status = OPENED

    def close(self):
        self.status = CLOSED

    def send(self, text, expectphrase):
        if self.status == CLOSED:
            raise Exception('connection not opened')
        self.recbuf = self.send_dict.get(text, '')
        if expectphrase not in self.recbuf:
            raise Exception('timed out')
