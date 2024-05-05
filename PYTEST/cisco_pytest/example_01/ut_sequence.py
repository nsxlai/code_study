import logging

from apollo.libs import lib
from apollo.libs import cesiumlib

CPU1_TEMP = 'CPU-1 temp'
LOG = logging.getLogger(__name__)


def ut_sequence_definition():
    seq = lib.SequenceDefinition('unittest_demo')
    seq.add_step(areacheck)
    seq.add_step(run_tests)
    return seq


def areacheck_original(serial_number, uut_type, prev_area):
    """Test step that does an areacheck.

        :param str serial_number: Serial number of the UUT that is being tested.
        :param str uut_type: uut_type of the UUT that is being tested.
        :param str prev_area: Area that should contain a pass record.
        """
    cesiumlib.verify_area(serial_number=serial_number, uut_type=uut_type, area=prev_area)
    return lib.PASS


def areacheck_middle(serial_number, uut_type, prev_area):
    """Test step that does an areacheck.

    :param str serial_number: Serial number of the UUT that is being tested.
    :param str uut_type: uut_type of the UUT that is being tested.
    :param str prev_area: Area that should contain a pass record.
    """
    try:
        cesiumlib.verify_area(serial_number=serial_number,
                              uut_type=uut_type,
                              area=prev_area)
    except Exception:
        return lib.FAIL, 'Failed areacheck.'
    return lib.PASS


def areacheck(prev_area):
    """Test step that does an areacheck.

    :param str prev_area: Area that should contain a pass record.
    """
    serial_number = lib.apdicts.userdict['serial_number']
    uut_type = lib.apdicts.userdict['uut_type']
    try:
        cesiumlib.verify_area(serial_number=serial_number, uut_type=uut_type, area=prev_area)
    except Exception:
        return lib.FAIL, 'Failed areacheck.'
    return lib.PASS


def run_tests():
    conn = lib.conn.uut
    conn.open()
    conn.send('run test1\n', expectphrase='#')
    if 'passed' not in conn.recbuf:
        conn.close()
        return lib.FAIL, 'test1 failed'
    conn.close()
    return lib.PASS

