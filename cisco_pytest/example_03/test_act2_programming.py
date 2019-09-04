import mock
from . import seq_steps as bakerstreet_steps



@mock.patch('menush.blade_program_act2')
@mock.patch('apollo.libs.lib.apdicts')
@mock.patch('apollo.libs.lib.getstepdata')
def test_program_act2(mock_stepdata, mock_apdicts, mock_program_act2):
    mock_certs = mock.MagicMock()

