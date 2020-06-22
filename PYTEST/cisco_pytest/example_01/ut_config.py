from apollo.libs import lib
from apollo.scripts.te_scripts.users.ianjoh.ut_demo import ut_sequence
from apollo.scripts.te_scripts.users.ianjoh.ut_demo import ut_pre_sequence

USERNAME = 'gen-apollo'
PASSWORD = 'Ad@pCr01!'
CONN_ARGS = dict(host='localhost', user=USERNAME, password=PASSWORD)


def ut_config():
    # SETUP PL, AREA, AND TS.
    machine_config = lib.get_station_configuration()
    pl = machine_config.add_production_line('unittest_demo')
    area = pl.add_area('PCBCEV')
    ts = area.add_test_station('ut_station')

    # PRESEQUENCE and SIMPLE PIDMAP
    ts.assign_pre_sequence(ut_pre_sequence.pre_sequence_definition)
    ts.add_pid_map(pid='DEMO', sequence_definition=ut_sequence.ut_sequence_definition)

    # SINGLE CONTAINER
    c = ts.add_container('demo_container')
    c.add_connection(name='uut', protocol='ssh', **CONN_ARGS)
