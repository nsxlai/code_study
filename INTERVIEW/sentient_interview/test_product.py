from . import product_lib
from mock import patch, MagicMock
from PYTEST import mark
import PYTEST


@mark.product_test
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductA_tcp_conn_direct(mock_tcp_connect_cm):
    uut_01_sn = 'ROC11111111'
    uut_01_pn = 'POWER-001A'
    uut_01 = product_lib.ProductA(uut_01_sn, uut_01_pn)
    sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_01_pn} \n Serial_Num: {uut_01_sn} \n EOL'
    mock_tcp_connect_cm.return_value: str = sim_server_output
    uut_01_output = uut_01.tcp_connect_cm(product_lib.HOST, product_lib.PORT, 'diag command1')  # third argument does not matter
    print(f'received: {uut_01_output}')
    assert uut_01_output == sim_server_output


@mark.product_test
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductA_get_data_1(mock_tcp_connect_cm):
    uut_02_sn = 'ROC12345HKK'
    uut_02_pn = 'POWER-002A'
    uut_02 = product_lib.ProductA(uut_02_sn, uut_02_pn)
    sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_02_pn} \n Serial_Num: {uut_02_sn} \n EOL'
    mock_tcp_connect_cm.return_value: str = sim_server_output
    uut_02_output = uut_02.get_data_1(product_lib.HOST, product_lib.PORT, 'diag command2', 'Num')
    print(f'received: {uut_02_output}')
    assert uut_02_output == ['Num', 'Num']


@mark.product_test
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductB_get_data_2(mock_tcp_connect_cm):
    uut_03_sn = 'ROC212330L5'
    uut_03_pn = 'POWER-001B'
    uut_03 = product_lib.ProductB(uut_03_sn, uut_03_pn)
    sim_server_output = f'Request data for UUT_01: \n Product_Num: {uut_03_pn} \n Serial_Num: {uut_03_sn} \n EOL'
    mock_tcp_connect_cm.return_value: str = sim_server_output
    uut_03_output = uut_03.get_data_2(product_lib.HOST, product_lib.PORT, 'diag command2')
    # print(f'received: {uut_03_output}')
    assert uut_03_output == \
           {'Request': 'data', 'for': 'UUT_01:', 'Product_Num:': 'POWER-001B', 'Serial_Num:': 'ROC212330L5', 'EOL': ''}


def tcp_connect_cm_good_output(server_ip_addr, server_port, command):
    print('\nThis is a mock function: Positive case')
    print(f'Mocking {server_ip_addr}:{server_port} with command {command}')
    mock_response = MagicMock()
    mock_response.return_value = 'Request data for UUT_01: \n Product_Num: GENERIC \n Serial_Num: GENERIC \n EOL'
    return mock_response.return_value


def tcp_connect_cm_bad_output(server_ip_addr, server_port, command):
    print('\nThis is a mock function: Negative case')
    print(f'Mocking {server_ip_addr}:{server_port} with command {command}')
    mock_response = MagicMock()
    mock_response.return_value = None
    return mock_response.return_value


conn_status_pass_case = [
    (['Diag Test'],  {'Diag': 'Test'}),
    ([None, 'Diag Test'], {'Diag': 'Test'}),
    ([None, None, 'Diag Test'], {'Diag': 'Test'}),
]


@mark.product_test
@mark.parametrize('tcp_connect_status, assert_output', conn_status_pass_case)
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductB_get_data_2_tcp_connect_retry_twice_pass(mock_tcp_connect_cm, tcp_connect_status, assert_output):
    uut_03_sn = 'ROC212330L5'
    uut_03_pn = 'POWER-001B'
    uut_03 = product_lib.ProductB(uut_03_sn, uut_03_pn)
    mock_tcp_connect_cm.side_effect = tcp_connect_status
    uut_03_output = uut_03.get_data_2(product_lib.HOST, product_lib.PORT, 'diag command2')
    assert uut_03_output == assert_output


conn_status_fail_case = [
    ([None, None, None, 'Diag Test'], {'Diag': 'Test'}),
]


@mark.product_test
@mark.negative_case
@mark.parametrize('tcp_connect_status, assert_output', conn_status_fail_case)
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductB_get_data_2_tcp_connect_retry_twice_fail(mock_tcp_connect_cm, tcp_connect_status, assert_output):
    uut_03_sn = 'ROC212330L5'
    uut_03_pn = 'POWER-001B'
    uut_03 = product_lib.ProductB(uut_03_sn, uut_03_pn)
    mock_tcp_connect_cm.side_effect = tcp_connect_status
    with PYTEST.raises(product_lib.GetData2Error):
        print('Raising GetData2Error due to retry fails after 2 times')
        uut_03.get_data_2(product_lib.HOST, product_lib.PORT, 'diag command2')


@mark.negative_case
def test_serial_number_bad_format():
    uut_02_sn = 'ROC12345'
    uut_02_pn = 'POWER-002A'
    with PYTEST.raises(ValueError):
        product_lib.ProductA(uut_02_sn, uut_02_pn)


@mark.negative_case
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductA_get_data_1_with_exception(mock_tcp_connect_cm):
    uut_02_sn = 'ROC12345HKK'
    uut_02_pn = 'POWER-002A'
    uut_02 = product_lib.ProductA(uut_02_sn, uut_02_pn)
    sim_server_output = f'request data for UUT_01: \n Product_Num: {uut_02_pn} \n Serial_Num: {uut_02_sn} \n EOL'
    mock_tcp_connect_cm.return_value: str = sim_server_output
    with PYTEST.raises(product_lib.GetData1Error):
        uut_02.get_data_1(product_lib.HOST, product_lib.PORT, 'diag command2', 'TEST')


@mark.negative_case
@patch.object(product_lib.BaseProduct, 'tcp_connect_cm')
def test_ProductB_get_data_2_with_exception(mock_tcp_connect_cm):
    uut_03_sn = 'ROC212330L5'
    uut_03_pn = 'POWER-001B'
    uut_03 = product_lib.ProductB(uut_03_sn, uut_03_pn)
    mock_tcp_connect_cm.return_value: str = ''
    with PYTEST.raises(product_lib.GetData2Error):
        uut_03.get_data_2(product_lib.HOST, product_lib.PORT, 'diag command2')
