import pytest
import threading

from apollo.engine import shared


class FakeTestInfo:
    def __init__(self):
        self.serial_number = 'serial_number'
        self.uut_type = 'uut_type'


@pytest.fixture()
def get_step_data(request):
    fresh_data = [dict(inputdict=dict(), outputdict=dict(), userdict=dict(), stepdict=dict())]
    shared.runningstepdata = dict()
    shared.runningstepdata[threading.current_thread().name] = fresh_data

    def cleanup():
        shared.runningstepdata[threading.current_thread().name] = fresh_data
    request.addfinalizer(cleanup)
    return shared.runningstepdata