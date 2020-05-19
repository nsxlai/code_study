all unit tests are written in a python file with a “test_” prefix
---
def areachck(serial_number, uut_type, prev_area)
    try: 
        cesiumlib.verify_area(serial_number=serial_number,
                                           uut_type=uut_type,
                                           area=prev_area)
    except Exception:
        return lib.FAIL, ‘Failed areacheck’
    return lib.PASS

@mock.patch.object(ut_sequence.cesiumlib. ‘verify_area’)
def test_areacheck(mock_verify_area):
    mock_verify_area.return_value = None
    assert lib.PASS == ut.sequence.areacheck(SERIAL_NUMBER, UUT_TYPE, PREV_AREA)
    mock_verify_area.assert_call_with(serial_number=SERIAL_NUMBER,
                                                            uut_type=UUT_TYPE,
                                                            area=PREV_AREA)

@mock.patch.object(ut_sequence.cesiumlib. ‘verify_area’)
def test_areacheck_failure(mock_verify_area):
    mock_verify_area.side_effect = Exception()
    assert (lib.FAIL, ‘Failed areacheck’) == ut.sequence.areacheck(SERIAL_NUMBER, UUT_TYPE, PREV_AREA)
    mock_verify_area.assert_call_with(serial_number=SERIAL_NUMBER,
                                                            uut_type=UUT_TYPE,
                                                            area=PREV_AREA)