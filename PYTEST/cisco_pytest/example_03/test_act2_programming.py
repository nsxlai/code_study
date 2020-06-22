from mock import patch
import mock
from . import seq_steps as bs_seq_steps
from . import menush
from PYTEST import mark


@patch.object(bs_seq_steps.lib, 'apdicts')
@patch.object(bs_seq_steps.cesiumlib, 'verify_area')
def test_areacheck_return_pass(_, __):
    result = bs_seq_steps.debug_areacheck()
    assert result == bs_seq_steps.lib.PASS


@patch.object(bs_seq_steps.lib, 'apdicts')
@patch.object(bs_seq_steps.cesiumlib, 'verify_area')
def test_areacheck_calls_verify_area(mock_verify_area, _):
    bs_seq_steps.debug_areacheck()
    assert mock_verify_area.called_once


@patch.object(bs_seq_steps.lib, 'apdicts')
@patch.object(bs_seq_steps.cesiumlib, 'verify_area')
def test_areacheck_calls_with_params(mock_verify_area, _):
    bs_seq_steps.debug_areacheck()
    mock_verify_area.assert_called_with(serial_number=mock.ANY,
                                        uut_type=mock.ANY,
                                        area=mock.ANY)


@patch.object(bs_seq_steps.lib, 'apdicts')
@patch.object(bs_seq_steps.cesiumlib, 'verify_area')
def test_areacheck_uses_userdict(mock_verify_area, mock_apdicts):
    mock_apdicts.userdict = {SERIAL_NUMBER: 'some_sn',
                             UUT_TYPE: 'some_pid',
                             PREV_AREA: 'some_area'}
    udict = mock_apdicts.userdict
    bs_seq_steps.debug_areacheck()
    mock_verify_area.assert_called_with(serial_number=udict[bs_seq_steps.SERIAL_NUMBER],
                                        uut_type=udict[bs_seq_steps.UUT_TYPE],
                                        area=udict[bs_seq_steps.PREV_AREA])



@patch.object(bs_seq_steps.lib, 'apdicts')
@patch.object(bs_seq_steps.cesiumlib, 'verify_area')
def test_areacheck_returns_fail(mock_verify_area, _):
    mock_verify_area.side_effect = bs_seq_steps.lib.apexceptions.ServiceFailure
    result = bs_seq_steps.debug_areacheck()
    assert result == bs_seq_steps.lib.FAIL


prog_status_pass_case = [
    [True],
    [False, True],
    [False, False, True],
]

prog_status_fail_case = [
    [False, False, False, True],
    [False, False, False],
]


@mark.parametrize('act2_prog_status', prog_status_pass_case)
@patch.object(menush, 'blade_program_act2')
@patch.object(bs_seq_steps.lib, 'apdicts')
@patch('apollo.libs.lib.getstepdata')
def test_program_act2_pass(_, __, mock_menush_program_act2, act2_prog_status):
    mock_menush_program_act2.side_effect = act2_prog_status
    result = bs_seq_steps.blade_program_act2()
    assert result == bs_seq_steps.lib.PASS


@mark.parametrize('act2_prog_status', prog_status_fail_case)
@patch.object(menush, 'blade_program_act2')
@patch.object(bs_seq_steps.lib, 'apdicts')
@patch('apollo.libs.lib.getstepdata')
def test_program_act2_fail(_, __, mock_menush_program_act2, act2_prog_status):
    mock_menush_program_act2.side_effect = act2_prog_status
    result = bs_seq_steps.blade_program_act2()
    assert result == bs_seq_steps.lib.FAIL
