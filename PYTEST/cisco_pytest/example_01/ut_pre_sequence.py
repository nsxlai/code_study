import random

from apollo.libs import lib


def pre_sequence_definition():
    seq = lib.SequenceDefinition('PRE SEQUENCE')
    seq.add_step(pre_seq_simple)
    return seq


def pre_seq_simple():
    info = lib.get_pre_sequence_info()
    container = info.containers[0]
    area = info.area
    uut_type = info.pids_by_area(area)[0]
    serial_number = 'IAN-{}'.format(random.randrange(100000, 999999, 1))
    lib.add_tst_data(serial_number=serial_number,
                     test_container=container,
                     uut_type=uut_type,
                     test_area=area)
    lib.apdicts.userdict['serial_number'] = serial_number
    lib.apdicts.userdict['uut_type'] = uut_type
    return lib.PASS
