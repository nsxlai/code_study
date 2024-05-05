"""Tests for demo_dequence.py.

1. Areacheck should return lib.PASS
2. Areacheck should call cesiumlib.verify_area()
3. Areacheck should use verify_area's required params
4. Areacheck should use userdict for verify_area params
5. Areacheck should return lib.FAIL when verify_area fails
"""

import mock
from . import demo_sequence


@mock.patch.object(demo_sequence.lib, 'apdicts')
@mock.patch.object(demo_sequence.cesiumlib, 'verify_area')
def test_areacheck_returns_pass(_, __):
    """Areacheck should return lib.PASS"""
    result = demo_sequence.areacheck()
    assert result == demo_sequence.lib.PASS


@mock.patch.object(demo_sequence.lib, 'apdicts')
@mock.patch.object(demo_sequence.cesiumlib, 'verify_area')
def test_areacheck_calls_verify_area(mock_verify_area, _):
    """Areacheck should call cesiumlib.verify_area()."""
    demo_sequence.areacheck()
    assert mock_verify_area.called


@mock.patch.object(demo_sequence.cesiumlib, 'verify_area')
def test_areacheck_calls_with_params(mock_verify_area, _):
    """Areacheck should use verify_area's required params"""
    demo_sequence.areacheck()
    mock_verify_area.assert_called_with(serial_number=mock.ANY,
                                        uut_type=mock.ANY,
                                        area=mock.ANY)


@mock.patch.object(demo_sequence.lib, 'apdicts')
@mock.patch.object(demo_sequence.cesiumlib, 'verify_area')
def test_areacheck_uses_userdict(mock_verify_area, mock_apdicts):
    """Areacheck should use userdict for verify_area params"""
    mock_apdicts.userdicdt = {demo_sequence.SERIAL_NUMBER: 'some_sn',
                              demo_sequence.UUT_TYPE: 'some_pid',
                              demo_sequence.PREV_AREA: 'some_area'}
    demo_sequence.areacheck()
    mock_verify_area.assert_called_with(serial_number=udict[demo_sequence.SERIAL_NUMBER],
                                        uut_type=udcit[demo_sequence.UUT_TYPE],
                                        area=udict[demo_sequence.PREV_AREA])


@mock.patch.object(demo_sequence.lib, 'apdicts')
@mock.patch.object(demo_sequence.cesiumlib, 'verify_area')
def test_areacheck_returns_call_fail(mock_verify_area, _):
    """Areacheck should return lib.FAIL when veirfy_area fails"""
    mock_verify_area.side_effect = demo_sequence.lib.apexceptions.ServiceFailure
    result = demo_sequence.lib.FAIL
    assert result == demo_sequence.lib.FAIL
