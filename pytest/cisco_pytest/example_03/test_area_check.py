import mock
from . import seq_steps as bakerstreet_steps


@mock.patch('apollo.libs.lib.apdicts')
@mock.patch.object(bakerstreet_steps, 'debug_message_display')
@mock.patch('apollo.libs.lib.get_apollo_mode')
@mock.patch('apollo.libs.cesiumlib.verify_area')
@mock.patch('apollo.libs.lib.getstepdata')
def test_verify_area(mock_stepdata, mock_verify, mock_ap_mode, mock_debug_message_display, mock_apdicts):
    # Test for DEBUG PID & SN
    mock_apdicts.userdict = {'uut_type':'DEBUG', 'sn':'DEBUG'}
    assert verify_area() == lib.PASS
    mock_debug_message_display.assert_called_once()

    # Test for DEBUG AP Mode
    mock_apdicts.userdict = {'uut_type':'REALPID1234', 'sn':'REALSN1234'}
    mock_ap_mode.return_value = 'DEBUG'
    assert verify_area() == lib.PASS
    assert not mock_verify.called, 'method should not be called when AP mode DEBUG'

    # Test Cesium Verify Area method
    mock_ap_mode.return_value = 'PROD'
    mock_apdicts.userdict['tan'] = 'REALTAN1234'
    mock_apdicts.userdict['area'] = 'SOME AREA'
    mock_apdicts.userdict['iterations'] = 'NUM OF LOOPS'
    assert verify_area(areas_to_check=['PCBP2']) == lib.PASS
    mock_verify.assert_called_once()
    mock_verify.assert_called_with(area='PCBP2', serial_number='REALSN1234', timeframe='30m', uut_type='REALTAN1234')

    # Negative Test Case
    mock_verify.side_effect = apexceptions.ServiceFailure
    assert verify_area() == lib.FAIL