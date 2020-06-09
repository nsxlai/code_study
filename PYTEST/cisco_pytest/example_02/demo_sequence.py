from apollo.libs import lib

SERIAL_NUMBER = 'serial_number'
UUT_TYPE = 'uut_type'
PREV_AREA = 'prev_area'


def areacheck():
    udict = lib.apdicts.userdict
    try:
        cesiumlib.verify_area(serial_number=udict[SERIAL_NUMBER],
                              uut_type=udict[UUT_TYPE],
                              prev_area=udict[PREV_AREA])
    except lib.apexceptions.ServiceFailure:
        return lib.FAIL
    return lib.PASS