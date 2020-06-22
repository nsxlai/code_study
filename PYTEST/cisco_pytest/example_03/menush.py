import re
import os
import time
import datetime
import logging
import types
import operator
from decimal import Decimal
from apollo.libs import lib, cesiumlib
from apollo.engine import apexceptions
from ...lib import util, gen_mac, lock

__version__ = '0.1'
log = logging.getLogger(__name__)
prompt = ['pad#', 'qpk#', 'kp#', 'qwy#']
resudi = False
sudi_prompt_retry = 3
resudi_prompt_retry = 3
certs = ['rsa', 'harsa']
act2_options = []
modulecmd = ''


def enter_menu(conn, expectphrase='MENUSH >', timeout=60, skip_fail_pars_list=False):
    """Enter menush

    As TDE, will enter menush prompt from diags prompt to execute menush commands

    :param conn: UUT Connection Object
    :param expectphrase: Phrase expected in response
    :timeout: Wait time in seconds
    :skip_fail_pars_list: Flag to catch error phrase. Default- False
    :return:
    """
    util.sende(conn=conn, text='menush\r', expectphrase=expectphrase, timeout=timeout)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)


def exit_menu(conn, expectphrase=prompt, timeout=60, skip_fail_pars_list=False):
    """Exit menush

    As TDE, will exit out of menush prompt to diags prompt to return to default diag prompt

    :param conn: UUT Connection Object
    :param expectphrase: Phrase expected in response
    :timeout: Wait time in seconds
    :skip_fail_pars_list: Flag to catch error phrase. Default- False
    :return
    """
    util.sende(conn=conn, text='quit\r', expectphrase=expectphrase, timeout=timeout)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)


def boot(conn, cmd, expectphrase=prompt, retry=0, timeout=200, skip_fail_pars_list=False):
    """Boot Diag

    As TDE, will boot diags from rommon env to execute diag commands/functions

    :param conn: UUT's connection Object
    :param cmd: Diag image name
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    """
    # Capture Diag Image to measurement list on Polaris DB
    util.upload_measurement(limit_name='Diag Image',
                            capture_value='{}'.format(cmd))
    """
    util.sende(conn, 'boot {}\r'.format(cmd), expectphrase=expectphrase, retry=retry, timeout=timeout)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    util.sende(conn, '\r', expectphrase=prompt)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot boot diags'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def set_mac(conn, expectphrase=prompt, timeout=200, retry=0, skip_fail_pars_list=False, **kwargs):
    """Set MAC

    As TDE, will configure uut mac settings to connect to network

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:
        - module - Module to display settings (eg .mgmt or br)
        - mac - UUT mac address to program
    :return result - Pass or Fail
    """
    userdict = lib.apdicts.userdict
    result = True

    module = kwargs['module']
    mac = kwargs['mac']

    util.sende(
        conn,
        'ifconfig {} hw ether {} \r' .format(module, mac),
        expectphrase=expectphrase,
        timeout=timeout,
        retry=retry,
    )

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False
    util.sleep(30)
    display_config(conn=conn,
                   expectphrase=expectphrase,
                   timeout=timeout,
                   retry=retry,
                   skip_fail_pars_list=skip_fail_pars_list,
                   module=module)

    if mac.upper() not in conn.recbuf:
        result = False
        log.info('MAC address not set.')

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to set MAC address'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def set_bridge(conn, expectphrase=prompt, timeout=200, retry=0, skip_fail_pars_list=False, **kwargs):
    """Set Bridge

    As TDE, will configure bridge mac and network settings to connect to network
    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required
        - mac - Bridge MAC
        - ip - Bridge ip address to program
        - netmask - Bridge netmask for network configuration
        - gateway - Bridge gateway for network configuration
    :return result - Pass or Fail
    """
    userdict = lib.apdicts.userdict
    result = True

    ip = kwargs['ip']
    netmask = kwargs['netmask']
    gateway = kwargs['gateway']

    # Set configuration twice
    for x in range(2):
        util.sende(conn, 'brctl addbr br\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
        util.sleep(5)
        util.sende(conn, 'ifconfig mgmt 0.0.0.0 down\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
        util.sende(conn, 'ifconfig eobc 0.0.0.0 down\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
        util.sleep(5)
        util.sende(conn, 'brctl addif br mgmt\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
        util.sende(conn, 'brctl addif br eobc\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
        util.sleep(5)
        result = set_network(conn,
                             timeout=timeout,
                             retry=retry,
                             skip_fail_pars_list=skip_fail_pars_list,
                             module='br',
                             ip=ip,
                             netmask=netmask,
                             gateway=gateway
                             )
        util.sleep(10)
        if result:
            util.sende(conn, 'ifconfig mgmt up\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sende(conn, 'ifconfig eobc up\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sende(conn, 'ifconfig mgmt up\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sende(conn, 'route add -net 10.1.0.0/24 br\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sleep(20)
        # Remove configuration only first time
        if x == 0:
            util.sende(conn, 'ifconfig br down\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sende(conn, 'brctl delbr br\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
            util.sleep(5)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to set bridge'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def set_network(conn, expectphrase=prompt, timeout=200, retry=0, skip_fail_pars_list=False, **kwargs):
    """Set Network

    As TDE, will configure uut network settings to connect to network

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
                    module: module to set configuration(example: mgmt, br etc) (String)
                    ip: ip address to program (String)
                    netmask: netmask for network configuration (String)
                    gateway: gateway for network configuration (String)
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    result = True

    module = kwargs['module']
    ip = kwargs['ip']
    netmask = kwargs['netmask']
    gateway = kwargs['gateway']

    util.sende(
        conn,
        'ifconfig {} {} netmask {} up\r' .format(module, ip, netmask),
        expectphrase=expectphrase,
        timeout=timeout,
        retry=retry,
    )

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    util.sende(
        conn,
        'route add -net 0.0.0.0 netmask 0.0.0.0 gw {}\r' .format(gateway),
        expectphrase=expectphrase,
        timeout=timeout,
        retry=retry,
    )

    if 'Network is unreachable' in conn.recbuf:
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - route table error'.format(util.whoami()),
            resolution_message='Review Server Address',
        )
        return result

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Other Errors'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def check_network(conn, expectphrase=prompt, timeout=200, retry=3, skip_fail_pars_list=False, **kwargs):
    """Check Network

    As TDE, Will ensure that network connection settings are proper and connection to network is made

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required
        - server - Server IP
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    result = True

    server = kwargs['server']

    util.sleep(30)  # Needed for time between route table add and ping
    util.sende(
        conn,
        'ping {} -c3\r' .format(server),
        expectphrase=expectphrase,
        timeout=timeout,
        retry=retry,
        regex=True
    )

    while '3 packets transmitted, 3 packets received' not in conn.recbuf:
        if retry > 0:
            util.sleep(30)
            retry -= 1
            util.sende(
                conn,
                'ping {} -c3\r' .format(server),
                expectphrase=expectphrase,
                timeout=timeout,
                retry=retry,
                regex=True
            )
        else:
            result = False
            break
        continue

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Network Error'.format(util.whoami()),
            resolution_message='Check Network Cable',
        )
    else:
        # Capture ping successfully to measurement list on Polaris DB
        util.upload_measurement(limit_name='Ping Successful',
                                capture_value=server)

    return result


def display_config(conn, expectphrase=prompt, timeout=200, retry=0, skip_fail_pars_list=False, **kwargs):
    """Display config settings

    As TDE, will display settings

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:
        - module - Module to display settings (eg .mgmt or br)
    :return result - Pass or Fail
    """
    module = kwargs['module']
    log.info('Display {} setting info'.format(module))
    util.sende(conn,
               'ifconfig {}\r'.format(module),
               expectphrase=expectphrase,
               timeout=timeout,
               retry=retry,
               )
    return


def verify_mac(mac_group='m', fetch_mac=True, skip_fail=False, **kwargs):
    """MAC

    Verify if given MAC Addres is legit, if not fetch a new one and return it

    :param mac_group: mac area to pull from
        ex. 'm' for production, 't' for lab.
        'a','b','e','m','n','o','p','q','r','t' (official list is lib.mac_groups)
    :param fetch_mac: Flag to fetch new mac . Default- True
    :param skip_fail: Flag to skip test failure. Default- False
    :param kwargs: Required:
                    sn:  sn attached to mac address (String)
                    uut_type:  uut type attached to mac address (String)
                    mac: mac to be verified (String)
                    block_size:  block size of mac address (Integer)
    :return:
    """
    sn = kwargs['sn']
    uut_type = kwargs['uut_type']
    mac = kwargs['mac']
    block_size = kwargs['block_size']
    formatted_mac = '{}'.format(''.join(re.findall(r'\w', mac))).strip()

    userdict = lib.apdicts.userdict
    result = True

    try:
        # Verify the MAC address, if any
        log.info('SN:        {}'.format(sn))
        log.info('PID:       {}'.format(uut_type))
        log.info('MAC:       {}'.format(formatted_mac))
        log.info('MAC Block: {}'.format(int(block_size)))

        log.info('Length of MAC: {}'.format(len(mac)))
        log.info('Searching MAC database to see if address: {} is legit'.format(formatted_mac))
        cesiumlib.verify_mac(
            sn,
            uut_type,
            formatted_mac,
            int(block_size)
        )
    # Existing MAC address Fails
    except (apexceptions.ResultFailure, apexceptions.ServiceFailure) as error_message:
        result = False
        log.info('MAC address: {} Verification FAILED.  Need to fetch an address'.format(formatted_mac))
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

        # Check to fetch New Mac address
        if fetch_mac:
            # Check for dummy MAC address
            mac_formats = [re.compile('fff?'), re.compile('bad?'), re.compile('^$'), re.compile('0000.*')]
            if any(regex.match(formatted_mac.lower()) for regex in mac_formats):
                log.info('--------------------------------')
                log.info('MAC Address {} matched fff* or bad* or empty formats.'.format(formatted_mac))
                log.info('Fetching MAC address.')
                result, formatted_mac, block_size = generate_mac(sn,
                                                                 uut_type,
                                                                 formatted_mac,
                                                                 block_size,
                                                                 mac_group,
                                                                 skip_fail
                                                                 )
            else:
                log.info('Fetching Prod MAC address.')
                result, formatted_mac, block_size = get_prod_mac(mac_group, skip_fail, **kwargs)
                log.info('Result of get_prod_mac: {}'.format(result))

            if result:
                start_mac = util.convert_mac_address(formatted_mac, 2, ':')
                log.info('--------------------------------')
                log.debug('MAC address fetched: {}, block size: {}'.format(start_mac, block_size))
                log.info('--------------------------------')

                # Record MAC in database
                result = record_mac(sn, uut_type, formatted_mac, block_size, skip_fail)

    # Exisiting MAC address Passes
    else:
        log.info('MAC address: {} is legit.  No need to fetch a new address'.format(formatted_mac))

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Wrong MAC address'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result, formatted_mac, block_size


def get_prod_mac(mac_group='m', skip_fail=False, **kwargs):
    """Get Prod MAC

    Fetch a New MAC Address, this function is part of verify_mac, had to split to reduce its cognitive complexity

    :param mac_group: mac area to pull from
        ex. 'm' for production, 't' for lab.
        'a','b','e','m','n','o','p','q','r','t' (official list is lib.mac_groups)
    :param skip_fail: Flag to skip test failure. Default- False
    :param kwargs: Required:
                    sn:  sn attached to mac address (String)
                    uut_type:  uut type attached to mac address (String)
                    mac: mac to be verified (String)
                    block_size:  block size of mac address (Integer)
    :return:
    """
    result = False
    sn = kwargs['sn']
    uut_type = kwargs['uut_type']
    mac = kwargs['mac']
    block_size = kwargs['block_size']
    formatted_mac = '{}'.format(''.join(re.findall(r'\w', mac))).strip()

    db_mac, db_uuttype = util.get_prod_mac(sn, items=['PID'])
    if db_mac and db_uuttype:
        if formatted_mac in db_mac and uut_type != db_uuttype:
            log.info('----------------------------------------------------------------')
            log.info('MAC ADDRESS {} MIGHT be legit but is recorded for different UUTTYPE.'.format(
                formatted_mac))
            log.info('----------------------------------------------------------------')
            result = True
        # Recorded UUT TYPE or MAC on PROD and UUT varies
        elif formatted_mac not in db_mac or uut_type != db_uuttype:
            log.info('----------------------------------------------------------------')
            log.info('MAC ADDRESS and UUTTYPE recorded are different.')
            log.info('Generating new MAC address.')
            log.info('----------------------------------------------------------------')
            result, formatted_mac, block_size = generate_mac(sn,
                                                             uut_type,
                                                             formatted_mac,
                                                             block_size,
                                                             mac_group,
                                                             skip_fail
                                                             )
        elif lib.get_apollo_mode() != 'PROD' or re.search('.*SJ.*|.*RTP.*|.*ENG.*',
                                                          lib.get_hostname().upper()):
            log.info('----------------------------------------------------------------')
            log.info('MAC ADDRESS {} MIGHT be legit but is not recorded in Staging.'.format(formatted_mac))
            log.info('----------------------------------------------------------------')
            result = True
    else:
        log.warning('MAC/UUTTYPE not in PROD or STAGING Database.')

    return result, formatted_mac, block_size


def generate_mac(sn, uut_type, mac, block_size, mac_group, skip_fail=False):
    """Generate MAC address based on the envirmoment PROD or DEBUG.

    :param sn: sn attached to mac address
    :param uut_type: uut type of the board/uut
    :param mac: mac address if it exists
    :param block_size: block size of mac address
    :param mac_group: mac area to pull from
        ex. 'm' for production, 't' for lab.
        'a','b','e','m','n','o','p','q','r','t' (official list is lib.mac_groups)
    param skip_fail: Flag to skip test failure. Default- False

    :return: result, mac, block_size
    """
    userdict = lib.apdicts.userdict
    result = False
    mac_file_path = '/tftpboot/mac'
    mac_file_name = 'mac.csv'

    log.info('Generating new MAC address..')
    # Fetch MAC address for Development from external MAC file
    if lib.get_apollo_mode() != 'PROD' or re.search('.*SJ.*|.*RTP.*|.*ENG.*', lib.get_hostname().upper()):
        mac_format = "string"
        # Initialize and acquire lock for MAC File
        lock.initialize_lock_state(name='MAC lock')
        result, result_msg = lock.acquire_lock(name='MAC lock')

        log.info('Accessing external mac file from local server at {}/{}.'.format(mac_file_path, mac_file_name))
        result, mac = gen_mac.generate_mac_external(
            mac_file_path,
            mac_file_name,
            int(block_size),
            sn,
            mac_format
        )
        # Release lock for MAC file
        try:
            lock.release_lock(name='MAC lock')
            lock.finalize_lock_state(name='MAC lock')
        except apexceptions.ApolloException:
            result = False
            log.warning('MAC Priority Lock Exceeded Release Timeout. Priority Lock Expired!')

    # Fetch MAC address in production mode
    else:
        try:
            log.info('Using cesiumlib fucntion to fetch valid MAC address.')
            mac, block_size = cesiumlib.generate_mac(sn, uut_type, int(block_size), mac_group)

        except (apexceptions.ResultFailure, apexceptions.ServiceFailure) as error_message:
            log.info('New MAC address cannot be fetched!')
            log.warning(error_message)
            if skip_fail:
                userdict['failed_sequences'][util.whoami()] = error_message
        else:
            result = True

    return result, mac, block_size


def record_mac(sn, uut_type, mac, block_size, skip_fail=False):
    """Record MAC

    :param sn: sn attached to mac address
    :param uut_type: uut type attached to mac address
    :param mac: mac address if it exists
    :param block_size: block size of mac address
    param skip_fail: Flag to skip test failure. Default- False
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    try:
        log.debug('Recording MAC address in database...')
        cesiumlib.record_mac(
            sn,
            uut_type,
            mac,
            int(block_size)
        )

    except (apexceptions.ResultFailure, apexceptions.ServiceFailure) as error_message:
        result = False
        log.info('MAC address not recorded.')
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

    return result


def mio_program_sprom(conn,
                      expectphrase=prompt,
                      retry=0,
                      timeout=200,
                      skip_fail_pars_list=False,
                      **kwargs):
    """Program MIO SPROM

    Routine to program mio children it will take the sprom_values dictionarie and will sent the program
    command for every item, also it consider the offset number in case the value needs to be programmed
    more than one time in the card.

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :kwargs - Required
            :param sprom_command: Module command used to program (Example: fru, pinner etc)
            :param sprom_key: Dictionary of IDPROM fields with format and offset info
                              (Example: {'CHASSIS SERIAL NUMBER': {'format': 'ascii', 'offset': ['19']}
                                        'PRODUCT NAME /PID': {'format': 'ascii', 'offset': ['51']}}
                              )
            :param sprom_values: Dictionary of IDPROM fields and IDPROM values to be programmed
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True

    sprom_command = kwargs['sprom_command']
    sprom_key = kwargs['sprom_key']
    sprom_values = kwargs['sprom_values']
    log.info('SPROM Values : {}'.format(sprom_values))

    for key in sprom_values:
        if 'SKIP' not in sprom_values[key]:
            for offset in sprom_key[key]['offset']:
                util.sende(
                    conn,
                    'diag mio utils idprom write -d {} -o {} -t {} -w {}\r'.format(
                        sprom_command,
                        offset,
                        sprom_key[key]['format'],
                        sprom_values[key].replace(" ", "")),
                    expectphrase=expectphrase,
                    retry=retry,
                    timeout=timeout,
                )
                # Check for parsing after send
                if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                    error_message = 'Error phrase found'
                    log.warning(error_message)
                    result = False

    util.sende(
        conn,
        'diag mio utils idprom checksum -d {}\r'.format(sprom_command),
        expectphrase=expectphrase,
        retry=retry,
        timeout=timeout,
    )
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to Program SPROM'.format(util.whoami()),
            resolution_message='Call Support',
        )
    return result


def blade_program_sprom(conn,
                        expectphrase=prompt,
                        timeout=200,
                        skip_fail_pars_list=False,
                        **kwargs):
    """Blade Program Sprom

    As TDE, will provide way to program sprom content for blade sprom verification

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param **kwargs: Required
                    :param sprom_keys: dictionary of sprom keys to program
                    :param sprom_values: dictionary of sprom values to program, pulled from fetch_cmpd_sprom
                    :param board_no: Slot of board
                    :param board: type of board


    :return: True or False
    """
    userdict = lib.apdicts.userdict
    result = True

    sprom_keys = kwargs['sprom_keys']
    sprom_values = kwargs['sprom_values']
    board_no = kwargs['board_no']
    board = kwargs['board']

    enter_menu(conn)
    try:
        for key1 in sprom_values:
            for key2 in sprom_keys:
                if key1 == key2[0] and 'SKIP' not in sprom_values[key1] and key2[1] != 'SKIP':

                    test_name = 'Program {}'.format(key1)
                    log.info('Test Name: {}'.format(test_name))

                    cmd = 'blade{}  program {}fields {} {}\r'.format(
                        board_no,
                        board,
                        key2[1],
                        '"' + sprom_values[key1] + '"',
                    )
                    log.info('Command: {}'.format(cmd))

                    result = run_functional_test(
                        conn=conn,
                        test_name=test_name,
                        test_command=cmd,
                        expectphrase='MENUSH >',
                        timeout=timeout,
                        skip_fail_pars_list=skip_fail_pars_list
                    )

                    if not result:
                        log.error('Unable to Program {} - {}'.format(board, key1))
                        userdict['operator_message'] = util.operator_message(
                            error_message='Error: {} - Unable to Program {} - {}'.format(util.whoami(), board, key1),
                            resolution_message='',
                        )
                        break
        exit_menu(conn)
    except Exception, error_message:
        log.error('Exception: {}'.format(str(error_message)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to Program {}'.format(util.whoami(), board),
            resolution_message='',
        )
        userdict['failed_sequences'][util.whoami()] = error_message
        result = False

    return result


# TODO: Why seperate function ? If required, need to modify parameter
def kilburn_program_sprom(conn, expectphrase=prompt, retry=0, timeout=10, skip_fail_pars_list=False, **kwargs):
    """ Program the values passed into the SPROM

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param sprom_values: Dictionary with values to program
    :param sprom_map: Sprom map values dictionary
    :return: True if Pass, False instead
    """
    userdict = lib.apdicts.userdict
    result = True

    sprom_values = kwargs['sprom_values']
    sprom_map = kwargs['sprom_map']

    for key in sprom_values:
        if sprom_values[key] != 'SKIP':
            util.sende(conn=conn,
                       text='diag mio utils idprom write data-d {}\r'.format(
                           filter(lambda x: x[0] == key, sprom_map)[0][1],
                           sprom_values[key]),
                       expectphrase=expectphrase,
                       retry=retry,
                       timeout=timeout,
                       )
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

    util.sende(conn=conn,
               text='diag mio utils idprom sync\r',
               expectphrase=expectphrase,
               retry=retry,
               timeout=timeout
               )
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error {} - Other Errors'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def mio_capture_sprom(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Capture SPROM

    As TDE, will define capture_sprom to get information from unit and capture into a dictionary.

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required
                 :param sprom_command: Module command used to program
                  (Example: 'fru' in 'mio utils idprom alter -d fru')
    :return:
    """
    sprom_values = []
    sprom_values_dict = {}
    sprom_command = kwargs['sprom_command']
    enter_menu(conn)
    sprom_command = 'mio utils idprom alter -d {} '.format(sprom_command)
    util.sende(conn, '{}\r'.format(sprom_command), '>', timeout=timeout)

    while True:
        if 'INFO: no more entries' in conn.recbuf:
            break
        key = re.search(r'\"(.*?)\"', conn.recbuf).group(1).strip(' \t\r\n\0')
        value = re.search(r'\[(.*?)\]', conn.recbuf).group(1).strip(' \t\r\n\0')[:512]
        value_hex = re.search(r'(?:@)([^\s]+)', conn.recbuf).group(1).strip(' \t\r\n\0')
        conn.sende(text='\r')
        conn.waitfor(expectphrase=['>', expectphrase], timeout=timeout)
        sprom_values_dict['{} - {}'.format(value_hex, key)] = str(value)
        sprom_values.append(str(value))

    log.info('Sprom Values: {}'.format('|'.join(sprom_values)))
    log.info('Sprom Dict: {}'.format(sprom_values_dict))

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)

    exit_menu(conn)
    return sprom_values, sprom_values_dict


def blade_capture_sprom(conn,
                        expectphrase=prompt,
                        timeout=200,
                        skip_fail_pars_list=False,
                        **kwargs):
    """Capture SPROM

    As TDE, will define capture_blade_sprom to get information from unit and capture into a dictionary.

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required
                 :param blade_no: Module Slot number
                 :param sprom_command: Command support in 'show' command
                                       (Example: 'bld' for 'diag blade1 show bldidprom')
                 :param display_key: List of IDPROM display key format
    :return:
    """
    sprom_values = []
    sprom_values_dict = {}

    blade_no = kwargs['blade_no']
    sprom_command = kwargs['sprom_command']
    display_key = kwargs['display_key']

    sprom_command = 'diag blade{} show {}idprom\r'.format(blade_no, sprom_command)
    util.sende(conn, '{}\r'.format(sprom_command), expectphrase, timeout=timeout)

    log.info('--Capturing SPROM values--')
    programmed_fields = lib.string_to_dict(conn.recbuf, ':')
    log.info('Programmed SPROM Fiels: {}'.format(programmed_fields))

    for key in display_key:
        log.info('{}:{}'.format(key, programmed_fields[key]))
        sprom_values_dict[key] = programmed_fields[key]
        sprom_values.append(programmed_fields[key])

    log.info('Sprom Values: {}'.format('|'.join(sprom_values)))
    log.info('Sprom Dict: {}'.format(sprom_values_dict))

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)

    return sprom_values, sprom_values_dict


def enter_act2_menu(conn, retry=0, timeout=10, skip_fail_pars_list=False, **kwargs):
    """Enter to the ACT2 menu and gets the actual mode

    :param conn: UUT's connection object
    :param retry: Number of retries
    :param timeout: Wait Time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: required
        :param modulecmd: Module's corresponding command to enter to ACT2 menu
    :return: True/False
    """
    modulecmd = kwargs['modulecmd']
    userdict = lib.apdicts.userdict
    result = True

    log.debug('--- Entering ACT2 Menu')
    util.sende(
        conn,
        'i2c {}0.70\r'.format(modulecmd),
        expectphrase=['Enter your selection:  [0]:', 'Select an option >'],
        retry=retry,
        timeout=timeout,
    )
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False
    else:
        userdict['actual_act2_mode'] = re.search(r'\b(HARSA|RSA)\b', conn.recbuf).group(1).upper()
    log.debug('--- Actual mode: {}'.format(userdict['actual_act2_mode']))

    return result


def exit_act2_menu(conn, expectphrase=prompt, retry=0, timeout=60, skip_fail_pars_list=False, **kwargs):
    """Send quit option to return to diag prompt

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:
         quit_cmd: Module's corresponding command to exit to ACT2 menu
    :return:
    """
    log.debug('--- Exiting ACT2 Menu')
    result = True
    quit_cmd = kwargs['quit_cmd']

    util.send(
        conn,
        '{}\r'.format(quit_cmd),
        expectphrase=expectphrase,
        retry=retry,
        timeout=timeout,
    )
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    return result


def program_act2(conn, expectphrase=prompt, retry=0, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Program Act2
    As TDE, will program Act2 on uut for cisco authentication

    :param certs: List of certificates to install
    :param modulecmd: Module's corresponding command to enter to ACT2 menu
    :param retry: Number of retries
    :param timeout: Wait Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
            - certs: List of certificates to be programmed
            - act2_options: ACT2 menu options
            - modulecmd: Slot Number (Applicable Only for EPM)
    :return True/False
    """
    userdict = lib.apdicts.userdict
    result = True
    global resudi
    global certs
    global act2_options
    global modulecmd

    certs = kwargs['certs'] if 'certs' in kwargs else certs
    act2_options = kwargs['act2_options'] if 'act2_options' in kwargs else act2_options
    modulecmd = kwargs['modulecmd'] if 'modulecmd' in kwargs else modulecmd

    # ACT2 Menu
    if not enter_act2_menu(conn=conn, modulecmd=modulecmd, retry=retry,
                           timeout=timeout, skip_fail_pars_list=skip_fail_pars_list):
        return False

    while retry >= 0:
        result = act2_login_and_cliip(conn=conn,
                                      act2_options=act2_options,
                                      timeout=timeout,
                                      skip_fail_pars_list=skip_fail_pars_list)
        if not result:
            retry -= 1
            continue
        for cert in certs:
            result = act2_sudi(conn=conn,
                               cert=cert,
                               act2_options=act2_options,
                               timeout=timeout,
                               skip_fail_pars_list=skip_fail_pars_list)
            if not result:
                break

        if result:
            resudi = False
            break

        retry -= 1

    # set status for cert recording
    status = 6 if result else 0

    # Upload Ruby SN into Polaris Measurement list.
    util.upload_measurement(limit_name='ACT2 Ruby SN',
                            capture_value='{}'.format(userdict['ruby_sn']))
    result = record_act2_sudi_cert_installation_status(ruby_sn=userdict['ruby_sn'], status=status)

    exit_act2_menu(conn=conn, expectphrase=expectphrase, quit_cmd=act2_options['quit'],
                   retry=retry, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list)

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Program ACT2 Failed'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def act2_login_and_cliip(conn, cert='rsa', act2_options={}, timeout=60, skip_fail_pars_list=False):
    """Perform mfg login as well as cliip steps (get, send and record cliip)

    :param conn: UUT's connection object
    :param cert: Initial cert the installation will start with
    :param act2_options: dictionary with act2 menu options
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    if not set_mode(conn=conn,
                    cert=cert,
                    mode_cmd=act2_options['set_mode'],
                    timeout=timeout,
                    skip_fail_pars_list=skip_fail_pars_list):
        return False
    result, ruby_sn = login_mfg_act2(conn=conn,
                                     mfg_login_cmd=act2_options['mfg_login'],
                                     skip_fail_pars_list=skip_fail_pars_list)
    if not result:
        return False
    userdict['ruby_sn'] = ruby_sn
    result, act2_cliip = get_cliip_act2(ruby_sn)
    if not result:
        return False
    result, identity_status = send_act2_cliip(conn=conn,
                                              install_identity_cmd=act2_options['install_identity'],
                                              cliip=act2_cliip,
                                              skip_fail_pars_list=skip_fail_pars_list)
    if identity_status == 12:
        record_act2_cliip_insertion_status(ruby_sn=ruby_sn, status=identity_status)
        return False
    if not result and identity_status != 6:
        return False
    if not record_act2_cliip_insertion_status(ruby_sn=ruby_sn, status=identity_status):
        return False

    return True


def act2_sudi(conn, cert='', act2_options={}, timeout=60, skip_fail_pars_list=False):
    """Will set the act2 cert mode and perform sudi and resudi(if required) certification steps

    :param conn: UUT's connection object
    :param cert: Cert to install
    :param act2_options: Dictionary with act2 menu options
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list:
    :return:
    """
    if not set_mode(conn=conn,
                    cert=cert,
                    mode_cmd=act2_options['set_mode'],
                    timeout=timeout,
                    skip_fail_pars_list=skip_fail_pars_list):
        return False
    if not get_act2_sudi_certificate(conn=conn,
                                     sudi_cert_cmd=act2_options['verify_indentity'],
                                     skip_fail_pars_list=skip_fail_pars_list):
        return False
    if not resudi:
        return True
    if not get_act2_resudi_certificate(conn=conn,
                                       resudi_cert_cmd=act2_options['verify_indentity'],
                                       skip_fail_pars_list=skip_fail_pars_list):
        return False
    return True


def verify_act2(conn, module, cert='rsa', timeout=900, skip_fail_pars_list=False):
    """Check ACT2 Authen
    As TDE,need to Check if MIO ACT2 is Installed or not

    :param conn:
    :param module:
    :param cert:
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict
    act2_info = {
        'rsa': {
            'tam': '0x1',
            'cert_type': '2019',
        },
        'harsa': {
            'tam': '0x3',
            'cert_type': '2099',
        },
    }

    result = run_functional_test(
        conn=conn,
        test_name='{} ACT2 Authen'.format(module),
        test_command='diag {} utils act2 authen cert-t {}'.format(module, act2_info[cert]['cert_type']),
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list
    )

    if not result:
        return result

    meas_phrase = ''
    act2_phrases = [
        'ACT-2 SUDI Installation Successful',
        'Certificate Type: {} SUDI'.format(cert.upper()),
        'cert_type = {}'.format(act2_info[cert]['tam'])
    ]
    log.info('ACT2 Expectphrases: {}'.format(act2_phrases))

    # if not using diag.2.0.1.0.SPA or above, this function will fail
    for phrase in act2_phrases:
        if phrase not in conn.recbuf:
            result = False
            log.error('{} not found!'.format(phrase))
        meas_phrase += '"{}" '.format(phrase)

    # Upload phrases to measurement link
    util.upload_measurement(limit_name='{} ACT2 Verification'.format(cert.upper()), capture_value=meas_phrase)
    capture_meas(conn.recbuf)
    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Other Errors'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def set_mode(conn, cert='rsa', mode_cmd='16', timeout=200, skip_fail_pars_list=False):
    """Set Mode

    As TDE, will set ACT2 certificate mode before programming ACT2

    :param conn:
    :param cert: Certificate type
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict
    log.info('---------------------------------------------')
    log.info('--- Changing ACT2 mode to {}'.format(cert))
    log.debug('--- Actual mode: {}'.format(userdict['actual_act2_mode']))
    result = True
    # will use the cert name as expectphrase cert_expectphrase = {'rsa': 'RSA-2019', 'harsa': 'HARSA-2099'}
    try:
        cert = cert.upper()
        if cert != userdict['actual_act2_mode']:
            util.send(
                conn,
                '{}\r'.format(mode_cmd),
                expectphrase=['Enter your selection:  [0]:', 'Select an option >'],
                timeout=timeout,
            )
            if not bool(re.search(r'\b{}\b'.format(cert), conn.recbuf)):
                log.warning('-- Unable to change Cert Mode to {}'.format(cert))
                return False
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)
                result = False
            userdict['actual_act2_mode'] = cert
            log.debug('--- {} mode is active now'.format(userdict['actual_act2_mode']))
            log.info('---------------------------------------------')
    except Exception as e:
        log.warning(e)
        result = False

    return result


def login_mfg_act2(conn, mfg_login_cmd, timeout=200, skip_fail_pars_list=False):
    """ACT2 MFG Login

    As TDE, will utilize the MFG login process to complete simple mode, ruby SN, act2 cert chain

    :param conn: UUT's connection object
    :param mfg_login_cmd: diag specifi command to enter the mfg login_mfg_act2
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    result = True
    key = 'ACT-2: serial number'
    nonce_key = 'Nonce Number is'
    nonce_len = 32
    split_size = 3400

    def __get_act2_certificate_chain():
        return cesiumlib.get_act2_certificate_chain()

    log.debug('INSIDE LOGIN MFG ACT2')
    log.info('---------------------------------------------')
    log.info('Calling cesium library to get the certificate chain')
    try:
        act2_certificate_chain = __get_act2_certificate_chain()
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        result = False
        return result
    else:
        log.info('Successfully executed certificate chain')
        log.info('---------------------------------------------')
        cert_chain_data = act2_certificate_chain[0]
        cert_chain_data_len = act2_certificate_chain[1]

    # MFG login command
    util.sende(
        conn,
        '{}\r'.format(mfg_login_cmd),
        expectphrase='Enter Nonce + cert chain length > [0]:',
        timeout=timeout,
    )
    ruby_sn = util.parse_for_key_value_pair(conn.recbuf, keys=[key], delimiter='=').get(key)
    log.debug('ruby_sn: {}'.format(ruby_sn))

    log.info('sending length of cert chain length + nonce: {}'.format(int(cert_chain_data_len) + nonce_len))
    util.sende(conn, '{}\r'.format(int(cert_chain_data_len) + nonce_len), expectphrase=['>'], timeout=timeout)

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    nonce_num = util.parse_for_key_value_pair(conn.recbuf, keys=[nonce_key], delimiter=':').get(nonce_key)
    log.info('nonce number captured: {}'.format(nonce_num))

    # critical to concatenate nonce with cert prior to generating signature
    challenge_data = '{}{}'.format(nonce_num, cert_chain_data)
    challenge_data_len = int(cert_chain_data_len) + int(nonce_len)

    log.info('---------------------------------------------')
    log.info('Calling cesium library to sign challenge data')
    try:
        sign_act2_challenge_data = cesiumlib.sign_act2_challenge_data(
            challenge_data,
            challenge_data_len
        )
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        result = False
        return result
    else:
        log.info('Successfully executed sign challenge data')
        log.info('---------------------------------------------')
        act2_signature = sign_act2_challenge_data[0]

    # send nonce + cert chain data
    challenge_data_list = [challenge_data[i:i + split_size] for i in range(0, len(challenge_data), split_size)]
    log.info('---------------------------------------------')
    for idx, data in enumerate(challenge_data_list):
        util.sende(conn, '{}\r'.format(data), expectphrase=['>'], timeout=timeout)
    log.info('---------------------------------------------')

    if 'tam_lib_mfg_login_credentials successfully' not in conn.recbuf:
        result = False
        return result
    else:
        log.info('successfully completed first step of mfg login')

    # send signature data
    log.debug('sending signature data: {}'.format(act2_signature))
    util.sende(conn, '{}\r'.format(act2_signature), expectphrase=['[0]:', '>'], timeout=timeout)
    if 'ACT-2 Manufacturing Login Successful' not in conn.recbuf:
        result = False
    else:
        log.info('successfully completed second step of mfg login')
        log.info('---------------------------------------------')

    return result, ruby_sn


def get_cliip_act2(ruby_sn):
    """ACT2 Get cliip

    As TDE, will get Cliip data for ACT2 process and programming

    :param ruby_sn - pulled from login_mfg_act2
    :return act2_cliip - Named tuple received from cesiumlib.get_act2_cliip
    :return result - Pass or Fail
    """
    result = True

    def __get_act2_cliip(act2_serial):
        return cesiumlib.get_act2_cliip(act2_serial)

    log.info('---------------------------------------------')
    log.info('Calling cesium library to get cliip data')

    try:
        act2_cliip = __get_act2_cliip(act2_serial=str(ruby_sn))
        log.debug('ACT2 CLIIP: ')
        util.display_string(act2_cliip)
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        result = False
        return result

    log.info('Successfully executed get cllip')
    log.info('---------------------------------------------')

    return result, act2_cliip


def send_act2_cliip(conn, install_identity_cmd, cliip, timeout=200, skip_fail_pars_list=False):
    """Send ACT2 cliip

    This does something for ACT2

    :param conn:
    :param install_identity_cmd: diag specific command to verify the identity
    :param cliip: cliip data pulled from get_cliip_act2
    :param timeout:
    :param skip_fail_pars_list:

    :return identity_status: Status return of the Identity Installation on UUT
    :return result: True or False
    """
    result = True
    identity_status = 6     # 6 - install successful

    cliip_data_len = cliip[1]
    cliip_data = cliip[0]
    split_size = 4000

    util.sende(conn, '{}\r'.format(install_identity_cmd), expectphrase=['[0]:'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # send cliip length
    util.sende(conn, '{}\r'.format(cliip_data_len), expectphrase=['data >'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # send cliip data
    cliip_data_list = [cliip_data[i:i + split_size] for i in range(0, len(cliip_data), split_size)]
    log.info('---------------------------------------------')
    for idx, data in enumerate(cliip_data_list):
        util.sende(conn, '{}\r'.format(data), expectphrase=['data >', '[0]:', 'option >'], timeout=timeout)
        if '*** Fatal error: the cliip data entered is' in conn.recbuf:
            log.info('Identity installation was not successful')
            result = False
            return result

        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False
    log.info('---------------------------------------------')

    if 'tam_lib_mfg_cliip_install returned with status 0x2e' in conn.recbuf:
        log.warning('Identity installation error 0x2e')
        identity_status = 12
        result = False
    elif 'ACT2 - Identity Installation Successful' in conn.recbuf:
        log.info('Identity installation was successful')
    else:
        log.warning('Identity installation failed')
        identity_status = 0     # 0 - Error in installation

    return result, identity_status


def record_act2_cliip_insertion_status(ruby_sn, status):
    """Record ACT2 cliip Insertion status

    As TDE, will report back to ACT2 database on insertation status of cliip

    :param ruby_sn: ATOM token that is pulled from login_mfg_act2
    :param status: The inseration status to pass along to the act2 database, pulled from send_act2_cliip

    :return: True or False
    """
    max_retry = 3

    def __record_act2_cliip_insertion_status(act2_serial, act2_status):
        return cesiumlib.record_act2_cliip_insertion_status(act2_serial, act2_status)

    # wrap status in a loop to get around 60003 errors
    for retry in range(0, max_retry):
        result = True
        log.info('---------------------------------------------')
        log.info('Calling cesium library to record cliip insertion status: {}'.format(status))
        try:
            __record_act2_cliip_insertion_status(act2_serial=str(ruby_sn), act2_status=status)
        except apexceptions.ServiceFailure as e:
            log.warning('Service Failure found: {}'.format(e))
            log.info('---------------------------------------------')
            if '60003' in e.message:
                log.warning('Error creating soap xml for csa.  Retrying')
                continue
            elif '13013' in e.message:
                log.warning('SUDI cert already exists')
                break
            else:
                result = False
                return result
        log.info('Successfully execute record insertion status')
        log.info('---------------------------------------------')
        break

    return result


def get_act2_sudi_certificate(conn, sudi_cert_cmd, timeout=200, skip_fail_pars_list=False):
    """Get ACT2 SUDI certificate

    As TDE, will insert the sudi certificate or issue a flag for resudi process

    :param conn:
    :param sudi_cert_cmd: Diag specific command to insert a SUDI certificate
    :param timeout:
    :param skip_fail_pars_list:

    :return: Pass or Fail
    """
    global sudi_prompt_retry
    max_retry = 3

    def __get_act2_sudi_certificate(act2_cms_data):
        return cesiumlib.get_act2_sudi_certificate(act2_cms_data)

    # wrap sudi in a for loop to give TE a chance to add PIDs to DB
    for retry in range(0, max_retry):
        result = True
        act2_sudi_cert = ()
        util.sende(conn, '{}\r'.format(sudi_cert_cmd), expectphrase=['[0]:'], timeout=timeout)

        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

        cms_data = re.search('(\(length is \d+\) =) (.+)', conn.recbuf).group(2).strip()
        log.debug('cms data: {}'.format(cms_data))

        log.info('---------------------------------------------')
        log.info('Calling cesium library to get sudi cert')
        try:
            act2_sudi_cert = __get_act2_sudi_certificate(act2_cms_data=cms_data)
        except apexceptions.ServiceFailure as e:
            log.warning('Service Failure found: {}'.format(e))
            log.info('---------------------------------------------')
            if not evaluate_sudi_error(e, conn, timeout, skip_fail_pars_list):
                return False
            elif resudi:
                log.info('Trying to ReSUDI.')
                return True
        else:
            log.info('Successfully execute sudi certificate')
            log.info('---------------------------------------------')
            break
    # tried to get sudi 3 times
    else:
        log.warning('Attemped to get SUDI three times.  Failing unit')
        result = False
        return result

    cert_len = act2_sudi_cert.sudi_cert_len
    cert_data = act2_sudi_cert.sudi_cert
    ca_root_len = act2_sudi_cert.sudi_ca_cert_len + act2_sudi_cert.sudi_root_cert_len
    ca_root_data = act2_sudi_cert.sudi_ca_cert + act2_sudi_cert.sudi_root_cert

    # SUDI cert
    util.sende(conn, '{}\r'.format(cert_len), expectphrase=['[0]:', '>'], timeout=timeout)
    util.sende(conn, '{}\r'.format(cert_data), expectphrase=['>', '[0]:'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # CA cert
    util.sende(conn, '{}\r'.format(ca_root_len), expectphrase=['[0]:', '>'], timeout=timeout)
    util.sende(conn, '{}\r'.format(ca_root_data), expectphrase=['>', '[0]:'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    if 'ACT-2 SUDI Installation Successful' not in conn.recbuf:
        log.warning('SUDI installation did not complete succesfully')
        result = False
    else:
        log.info('SUDI installation completed succesfully')

    return result


def get_act2_resudi_certificate(conn, resudi_cert_cmd, timeout=200, skip_fail_pars_list=False):
    """Get ACT2 resudi certificate

    As TDE, will issue a resudi process in the event that a sudi certificate cannot be generated

    :param conn:
    :param resudi_cert_cmd: Diag specific command to issue a resudi certificate
    :param timeout:
    :param skip_fail_pars_list:

    :return: Pass or Fail
    """
    global resudi_prompt_retry, resudi
    max_retry = 3

    def __get_act2_resudi_certificate(act2_cms_data):
        return cesiumlib.get_act2_resudi_certificate(act2_cms_data)

    # wrap sudi in a for loop to give TE a chance to add PIDs to DB
    for retry in range(0, max_retry):
        result = True
        act2_sudi_cert = ()
        util.sende(conn, '{}\r'.format(resudi_cert_cmd), expectphrase=['[0]:'], timeout=timeout)

        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

        cms_data = re.search('(\(length is \d+\) =) (.+)', conn.recbuf).group(2).strip()
        log.debug('cms data: {}'.format(cms_data))

        log.info('---------------------------------------------')
        log.info('Calling cesium library to get reSUDI cert')
        try:
            resudi = False
            act2_sudi_cert = __get_act2_resudi_certificate(act2_cms_data=cms_data)
        except apexceptions.ServiceFailure as e:
            log.warning('Service Failure found: {}'.format(e))
            log.info('---------------------------------------------')
            if not evaluate_resudi_error(e, conn, timeout, skip_fail_pars_list):
                return False
        # else:
        log.info('Successfully execute reSUDI certificate')
        log.info('---------------------------------------------')
        break
    # tried to get sudi 3 times
    else:
        log.warning('Attemped to get reSUDI three times.  Failing unit')
        result = False
        return result

    cert_len = act2_sudi_cert.sudi_cert_len
    cert_data = act2_sudi_cert.sudi_cert
    ca_root_len = act2_sudi_cert.sudi_ca_cert_len + act2_sudi_cert.sudi_root_cert_len
    ca_root_data = act2_sudi_cert.sudi_ca_cert + act2_sudi_cert.sudi_root_cert

    # SUDI cert
    util.sende(conn, '{}\r'.format(cert_len), expectphrase=['>', '[0]:'], timeout=timeout)
    util.sende(conn, '{}\r'.format(cert_data), expectphrase=['>', '[0]:'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # CA cert
    util.sende(conn, '{}\r'.format(ca_root_len), expectphrase=['[0]:', '>'], timeout=timeout)
    util.sende(conn, '{}\r'.format(ca_root_data), expectphrase=['>', '[0]:'], timeout=timeout)

    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    if 'ACT-2 SUDI Installation Successful' not in conn.recbuf:
        log.warning('SUDI installation did not complete succesfully')
        result = False
    else:
        log.info('SUDI installation completed succesfully')

    return result


def evaluate_sudi_error(e, conn, timeout=200, skip_fail_pars_list=False):
    """Evaluate SUDI Error

    As TDE, will need a function to evaluate Exception on ReSUDI

    :param e: Exception
    :param conn: Container Connection
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    global resudi
    result = True
    # Infrastructure error
    if '60003' in e.message:
        exit_to_act2_menu(conn, timeout, skip_fail_pars_list)
        result = False
    # reSUDI required
    elif '13023' in e.message:
        exit_to_act2_menu(conn, timeout, skip_fail_pars_list)
        resudi = True
        # do not set result to fail.  resudi is needed. this does not mean the unit should fail
        return result
    # ATOM SN not entered into CBE for this PID
    elif '13026' in e.message:
        # log.debug('data type: {}'.format(error_message.message))
        log.warning('Error 13026 found.  Token SN not currently in CBE')
        # capture token SN + PID
        token_sn = re.search('(Token with serial \()([a-f0-9]+)(\))', e.message).group(2).strip()
        token_pid = re.search('(PID:)([\d\w-]*)(!)', e.message).group(2).strip()
        result = retry_sudi(token_sn, token_pid, conn, timeout, skip_fail_pars_list)
    else:
        log.warning('Not sure what is wrong.  Failing unit')
        result = False

    return result


def evaluate_resudi_error(e, conn, timeout=200, skip_fail_pars_list=False):
    """Evaluate ReSUDI Error

    As TDE, will need a function to evaluate Exception on ReSUDI

    :param e: Exception
    :param conn: Container Connection
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    # Infrastructure error
    if '60003' in e.message:
        exit_to_act2_menu(conn, timeout, skip_fail_pars_list)
        result = False

    # ATOM SN not entered into CBE for this PID
    elif '13018' in e.message:
        log.warning('Error 13018 found.  Token SN not allowed to resudi')
        # capture token SN + PID
        token_sn = re.search('(Token with serial \()([a-f0-9]+)(\))', e.message).group(2).strip()
        from_pid = re.search('(transforming PID:)([\d\w-]*) ()', e.message).group(2).strip()
        to_pid = re.search('(to PID:)([\d\w-]*)(!)', e.message).group(2).strip()
        result = retry_resudi(token_sn, from_pid, to_pid, conn, timeout, skip_fail_pars_list)
    else:
        log.warning('Not sure what is wrong.  Failing unit')
        result = False

    return result


def exit_to_act2_menu(conn, timeout=200, skip_fail_pars_list=False):
    """Exit To ACT2 Menu

    Send dummy data until prompt returns to act2 prompt

    :param conn:
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    for i in range(1, 5):
        util.sende(conn, '{}\r'.format(i), expectphrase=['[0]:', '>'], timeout=timeout)

        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)

    log.warning('Error creating soap xml for csa')


def retry_sudi(token_sn, token_pid, conn, timeout=200, skip_fail_pars_list=False):
    """Retry SUDI

    As TDE, need a function to retry SUDI when it fails

    :param token_sn:
    :param token_pid:
    :param conn:
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    global sudi_prompt_retry

    while True:
        if sudi_prompt_retry > 0:
            sudi_prompt_retry -= 1
            response = lib.ask_question(
                'Call TE!!! PID: {} not entered in CBE for token: {}.  Enter "N/Y" when ready'.format(
                    token_pid,
                    token_sn
                )
            ).upper()
            if 'N' in response:
                log.warning('PID: {} not entered in CBE for token: {}'.format(token_pid, token_sn))
                return False
            elif 'Y' in response:
                # retry sudi
                log.warning('Retrying to SUDI')
                util.send(conn, '\x03\r', expectphrase=prompt, timeout=timeout)

                if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                    error_message = 'Error phrase found'
                    log.warning(error_message)
                    return False

                return program_act2(conn, retry=1)
            else:
                continue
        else:
            log.warning('PID: {} not entered in CBE for token: {} after {} try.'.format(
                token_pid,
                token_sn,
                sudi_prompt_retry
            ))
            return False


def retry_resudi(token_sn, from_pid, to_pid, conn, timeout=200, skip_fail_pars_list=False):
    """Retry ReSUDI

    As TDE, need a function to retry ReSUDI when it fails

    :param token_sn:
    :param from_pid:
    :param to_pid:
    :param conn:
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """
    global resudi_prompt_retry

    while True:
        if resudi_prompt_retry > 0:
            resudi_prompt_retry -= 1
            response = lib.ask_question(
                'Call TE!! RESUDI not allowed from PID: {} to PID: {} for token: {}.Enter "N/Y" when ready'.format(
                    from_pid,
                    to_pid,
                    token_sn
                )
            ).upper()
            if 'N' in response:
                log.warning('RESUDI not allowed from PID: {} to PID: {} for token: {}'.format(
                    from_pid,
                    to_pid,
                    token_sn
                ))
                return False
            elif 'Y' in response:
                # retry resudi
                log.warning('Retrying to reSUDI')
                util.send(conn, '\x03\r', expectphrase=prompt, timeout=timeout)

                if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                    error_message = 'Error phrase found'
                    log.warning(error_message)
                    return False

                return program_act2(conn, retry=1)
            else:
                continue
        else:
            log.warning('RESUDI not allowed from PID: {} to PID: {} for token: {} after {} try'.format(
                from_pid,
                to_pid,
                token_sn,
                resudi_prompt_retry
            ))
            return False


def record_act2_sudi_cert_installation_status(ruby_sn, status):
    """Record ACT2 SUDI certificate installation status

    As TDE, will report back to act2 database on sudi certificate installation status

    :param ruby_sn - ATOM token that is pulled from login_mfg_act2
    :param status - The inseration status to pass along to the act2 database, pulled from send_act2_cliip
    :param result - Pass or Fail
    """
    max_retry = 3

    def __record_act2_sudi_cert_installation_status(act2_serial, act_status):
        return cesiumlib.record_act2_sudi_cert_installation_status(act2_serial, act_status)

    # wrap status in a loop to get around 60003 errors
    for retry in range(0, max_retry):
        result = True
        log.info('---------------------------------------------')
        log.info('Calling cesium library to record sudi insertion status: {}'.format(status))
        try:
            __record_act2_sudi_cert_installation_status(act2_serial=str(ruby_sn), act_status=status)
        except apexceptions.ServiceFailure as e:
            log.warning('Service Failure found: {}'.format(e))
            log.info('---------------------------------------------')
            if '60003' in e.message:
                log.warning('Error creating soap xml for csa.  Retrying')
                continue
            else:
                result = False
                return result
        # else:
        log.info('Successfully execute sudi insertion status')
        log.info('---------------------------------------------')
        break

    return result


def blade_init(conn, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Blade Init

        As TDE, connect to blade and set blade network configuration
         :param conn: UUT's connection Object
         :param expectphrase: Phrase expected in response
         :param timeout: Wait time in seconds
         :param skip_fail_pars_list: Flag to catch error phrase. Default- False
         :param kwargs: Required
            :param: module: Module Slot no
            :param: ip_prefix: Server's IP prefix
            :param: blade_ip_suffix: UUT's Blade IP suffix
            :param: netmask: Server's netmask
            :param: gateway: Server's gateway
    """
    userdict = lib.apdicts.userdict
    result = True
    try:
        module_no = kwargs['module_no']
        ip_prefix = kwargs['ip_prefix']
        blade_ip_suffix = kwargs['blade_ip_suffix']
        netmask = kwargs['netmask']
        gateway = kwargs['gateway']

        log.info('-----Connecting to Blade via Telnet (127.3.0.{})-----'.format(module_no))
        util.sende(conn, 'telnet 127.3.0.{}\r'.format(module_no), 'CISCO-IBMC login:', timeout=timeout)
        util.sende(conn, 'root\r')
        util.sleep(10)
        util.sende(conn, '\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
        log.info('-----Connected to Blade (127.3.0.{})-----'.format(module_no))
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)

        util.send(
            conn,
            'ifconfig eth0 {}{} netmask {}\r'.format(ip_prefix,
                                                     blade_ip_suffix,
                                                     netmask),
            'IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
        )
        util.send(conn,
                  'route add -net 10.1.0.0/24 dev eth0\r',
                  'IBMC-SLOT\[.*\] #',
                  timeout=timeout,
                  regex=True)

        util.send(conn,
                  'route add default gw {}\r'.format(gateway),
                  'IBMC-SLOT\[.*\] #',
                  timeout=timeout,
                  regex=True)

        result = check_network(conn, expectphrase='IBMC-SLOT\[.*\] #', retry=3, server=kwargs['server'])
    except Exception, e:
        log.error('Unable to initialize blade network - {}'.format(str(e)))
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unit unable to initialize blade'.format(util.whoami()),
            resolution_message='',
        )

    return result


def exit_to_host(conn, timeout=200, skip_fail_pars_list=False):
    """ Exit from MIO/supervisor board to the Server (Apollo machine)
    :param conn: UUT's connection object
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    try:
        log.info('-----Exit to host prompt-----')
        prompt = util.sende(conn, '\r', timeout=timeout)
        if not re.match(r'gen-apollo@.*$', prompt):
            util.sende(conn,
                       'exit\r',
                       'gen-apollo@.*$',
                       timeout=timeout,
                       regex=True)
            util.sleep(10)
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                log.warning('Error phrase found')
                result = False
                log.info('-----In host-----')
    except Exception:
        log.error('Unable to exit to host')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unit unable exit to host'.format(util.whoami()),
            resolution_message='',
        )
        result = False

    return result


def mio_connect(conn, expectphrase=prompt, timeout=200, **kwargs):
    """MIO Connect

    SSH connect to an MIO from server (10.1.1.1) using dummy connection

    :param conn: UUT's connection object
    :param prompt: Diag prompt by default
    :param kwargs: Required
                 - ip_prefix: Prefix of the Supervisor IP
                 - mio_ip_suffix: Management IP suffix of the Supervisor
                 - credentials: User credentials - {'id': username, 'password': password}
    :return:
    """
    userdict = lib.apdicts.userdict
    try:
        username = kwargs['credentials']['id']
        ip_prefix = kwargs['ip_prefix']
        mio_ip_suffix = kwargs['mio_ip_suffix']

        # If Remote TS use then tunnel into proper 10.1.1.1 server
        if lib.get_cached_data('remote_ts_{}'.format(lib.get_container_name())) is not None:
            enter_remote_server(conn, **kwargs)
        util.sende(conn, '\r')
        util.sleep(10)

        if any(regex in conn.recbuf for regex in expectphrase):
            return True
        # Test Connection Prior to use
        if re.search(r'{}@.*$'.format(username), conn.recbuf):
            util.sende(conn, 'ping {}{} -c5\r'.format(ip_prefix, mio_ip_suffix),
                       '--- {}{} ping statistics ---'.format(ip_prefix, mio_ip_suffix), timeout=timeout)
            util.sleep(10)

            if '0% packet loss' not in conn.recbuf:
                userdict['operator_message'] = util.operator_message(
                    error_message='Error: {} - Cannot ping to {}{}'.format(util.whoami(), ip_prefix, mio_ip_suffix),
                    resolution_message='Call Support',
                )
                return False

            # Enter Unit Under Test on private network
            util.sende(conn, '\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
            util.sende(conn,
                       'ssh {}{}\r'.format(ip_prefix, mio_ip_suffix),
                       expectphrase=['.*password.*', '(yes/no)'],
                       regex=True,
                       timeout=timeout)
            if '(yes/no)' in conn.recbuf:
                util.sende(conn, 'yes\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
            util.sende(conn, '\r', expectphrase=expectphrase, timeout=timeout)
            log.info('SSH Connected to {}{} (MIO)'.format(ip_prefix, mio_ip_suffix))
    except Exception, e:
        log.error('Error on Connecting to MIO')
        log.error('Error: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to connect to MIO via SSH'.format(util.whoami()),
            resolution_message='',
        )
        return False

    return True


def blade_connect(conn, timeout=600, skip_fail_pars_list=False, **kwargs):
    """ Blade Connect
        As TDE, need a function to connect via Telnet from the MIO to a Blade
        :param conn: UUT's connection object
        :param mio_ip: UUT's MIO IP suffix
        :param blade_ip: UUT's Blade IP suffix
        :param expectphrase: expected phrase/value
        :param timeout: Wait time in seconds
        :param skip_fail_parse_list: Ignore any error/fail message if True
        :param kwargs: Required
                     - ip_prefix: Prefix of the Supervisor IP
                     - mio_ip: Management IP suffix of the Supervisor
                     - blade_ip: UUT's Blade IP suffix
                     - credentials: User credentials - {'id': username, 'password': password}
        :return
        """
    userdict = lib.apdicts.userdict
    result = True
    try:
        log.info('-----Connecting to Blade via Telnet-----')
        blade_ip_suffix = kwargs['blade_ip_suffix']

        prompt = util.sende(conn, '\r')
        if re.match('IBMC-SLOT\[.*\] #', prompt):
            return
        result = mio_connect(conn, **kwargs)
        if result:
            util.sende(conn, 'telnet 10.1.1.{}\r'.format(blade_ip_suffix), 'login:', timeout=timeout)
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                log.warning('Error phrase found')
                result = False

            util.sende(conn, 'root\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
                log.warning('Error phrase found')
                result = False
            log.info('-----Telnet Connected to 10.1.1.{} (Blade)-----'.format(blade_ip_suffix))
    except Exception, e:
        result = False
        log.error('Error on Connecting to Blade')
        log.error('Error: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to connect to blade'.format(util.whoami()),
            resolution_message='',
        )

    return result


def blade_program_act2(conn, prompt=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Blade Program Act2
    As TDE, will program Act2 on blade for cisco authentication
    :param conn: UUT's connection
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list:
    :param kwargs: Required:
            - cert: List of certifications to install
            - sn: UUT's serial number
            - bin_image: Binary image name for ACT2 certificate installation
            - module_no: Blade's slot number
            - ip_prefix: Server's IP prefix
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - netmask: Server's netmask
            - gateway: Server's gateway
            - server: Server IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return True or False
    """
    userdict = lib.apdicts.userdict
    result = False
    global resudi

    cert = kwargs['cert'] if 'cert' in kwargs else ['rsa', 'ecc', 'harsa']

    if not blade_generate_act2_cert(conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return False

    if not blade_get_session_id(conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return False

    if not blade_install_cliip(conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return False

    for cert_type in cert:
        result = blade_install_sudi(
            conn=conn,
            cert_type=cert_type,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list,
            **kwargs
        )
        if resudi:
            result = blade_install_resudi(
                conn=conn,
                cert_type=cert_type,
                timeout=timeout,
                skip_fail_pars_list=skip_fail_pars_list,
                **kwargs
            )
            resudi = False
    if result:
        result = blade_verify_certificates(
            conn=conn,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list,
            **kwargs
        )

    # set status for cert recording
    status = 6 if result else 0
    result = record_act2_sudi_cert_installation_status(userdict['chip_sn'], status)

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Program Blade ACT2 Failed'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def blade_verify_act2(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ ACT2 Necessary
    As TDE, need a function to verify if ACT2 is already installed or not in a Blade
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - conn: UUT's connection
            - bin_image: Binary image name for ACT2 certificate installation
            - module_no: Blade's slot number
            - ip_prefix: IP prefix used to connect to the Blade
            - blade_ip_suffix: UUT's Blade IP suffix
            - netmask: Server's netmask
            - gateway: Server's gateway
            - server: Server IP
    :return True or False
    """
    log.info('---Verifying ACT2 Status---')
    userdict = lib.apdicts.userdict
    image = kwargs['bin_image']
    need_act2 = True
    result = True

    log.info('Bin Image: {}'.format(image))

    try:
        if not blade_init(
            conn=conn,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list,
            **kwargs
        ):
            return need_act2, False

        util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout, regex=True)
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            log.warning('Error phrase found')
            result = False

        # Get bin image
        util.send(
            conn,
            'cp -p /opt/cisco/bin/Secure-Action {}\r'.format(image),
            'IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
        )
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            log.warning('Error phrase found')
            result = False

        util.send(
            conn,
            'chmod 777 {}\r'.format(image),
            'IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
        )
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            log.warning('Error phrase found')
            result = False

        util.send(
            conn,
            '/tmp/{} --action tam-get-info --tam-chip-id 0\r'.format(image),
            'IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
        )
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            log.warning('Error phrase found')
            result = False

        auth_status_response = conn.recbuf
        if 'Authentication Status: Success' in auth_status_response:
            log.info('ACT2 already installed')
            need_act2 = False

        chip_sn = ''
        for auth_line in auth_status_response.splitlines():
            if 'CSN' in auth_line:
                chip_sn = auth_line.split('=')[1].strip()
                break

        if chip_sn == '':
            log.error('Cannot get Chip SN from recbuf\n{}'.format(auth_status_response))
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {}'.format(util.whoami()),
                resolution_message='Call Support',
            )
            result = False

        userdict['chip_sn'] = chip_sn
        log.info('Chip Serial Number is: {}'.format(chip_sn))

        util.send(conn, 'exit\r', expectphrase, timeout=timeout)

    except Exception, e:
        log.error('Cannot determine if ACT2 is necessary'.format(str(e)))
        log.error('Catched Error on ACT2 Status Validation: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        result = False

    log.debug('Unit needs ACT2?: {}'.format(need_act2))
    log.info('---ACT2 Status Validated---')

    return need_act2, result


def blade_generate_act2_cert(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Generate ACT2 Cert

    As TDE, need a function to request for CertChain and init session on a Blade

    :param conn: UUT connection
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - sn: UUT's serial number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return True or False
    """
    log.info('-----Gen ACT2 Cert-----')
    userdict = lib.apdicts.userdict
    result = True

    sn = kwargs['sn']
    image = kwargs['bin_image']
    server_ip = kwargs['server']

    if not blade_get_cert_chain(conn, timeout, skip_fail_pars_list, **kwargs):
        return False

    # Login for Step 1
    util.send(conn, '/tmp/{} --action tam-mfg-login-step-1 '.format(image) +
              '--tam-login-cert my_cert_chain_{0}.txt --tam-out-file to_be_signed_{0}.txt '.format(sn) +
              '--tam-chip-id 0\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    log.info('MFG login status: {}'.format(conn.recbuf))
    if not util.response_success(conn.recbuf):
        log.error('Mfg Login Step 1 Status Not Found')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    util.send(conn, 'tftp -r /to_be_signed_{}.txt -p {}\r'.format(sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'exit\r', expectphrase, timeout=timeout)
    exit_to_host(conn=conn)

    util.send(conn, 'cd /tftpboot\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='to_be_signed_{}.txt'.format(sn),
            prompt='gen-apollo@.*$',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    util.send(conn, 'cat to_be_signed_{}.txt\r'.format(sn), 'gen-apollo@.*$', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    to_be_signed_dict = util.parse_for_key_value_pair(buffer=conn.recbuf, delimiter='=')
    challenge_data = to_be_signed_dict['challengeData']
    challenge_data_len = to_be_signed_dict['challengeDataLen']

    log.debug('Challenge Data Len Expected: {}'.format(challenge_data_len))
    log.debug('Challenge Data Len Recieved: {}'.format(len(challenge_data) / 2))
    log.debug('Challenge Data: ')
    util.display_string(challenge_data)

    if int(challenge_data_len) != len(challenge_data) / 2:
        log.warning('Mismatch Challenge Data Length. Expected: {}, Recieved: {}'.format(challenge_data_len,
                                                                                        len(challenge_data) / 2))
        return False

    # Sign Certificate
    # -----CESIUMLIB-----
    def __sign_act2_challenge_data(challenge_data, challenge_data_len):
        return cesiumlib.sign_act2_challenge_data(challenge_data, challenge_data_len)

    log.info('---------------------------------------------')
    log.info('Calling cesium library to sign challenge data')
    try:
        sign_act2_challenge_data = __sign_act2_challenge_data(
            challenge_data,
            challenge_data_len
        )
        for k in sign_act2_challenge_data:
            log.debug('C Data: {}'.format(k))
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False
    else:
        log.info('Successfully executed sign challenge data')
        log.info('---------------------------------------------')
        act2_signature = sign_act2_challenge_data[0]
        act2_signature_len = sign_act2_challenge_data[1]

        log.debug('ACT2 Signature Length Expected: {}'.format(act2_signature_len))
        log.debug('ACT2 Signature Length Recieved: {}'.format(len(act2_signature) / 2))
        log.debug('ACT2 Signature: ')
        util.display_string(act2_signature)

        if int(challenge_data_len) != len(challenge_data) / 2:
            log.warning('Mismatch Challenge Data Length. Expected: {}, Recieved: {}'.format(challenge_data_len,
                                                                                            len(challenge_data) / 2))
            return False

    # Gen file signed_data_{}.txt
    try:
        filepath = os.path.join('/tftpboot', 'signed_data_{}.txt'.format(sn))
        signed_file = open(filepath, 'a+')
        os.chmod(filepath, 0o777)
        signed_file.write('\n\nResponse Status: SUCCESS\n\n\n====== Response Begin ======\n\n')
        signed_file.write('SignatureLen={}\n'.format(act2_signature_len))
        signed_file.write('Signature={}\n'.format(act2_signature))
        signed_file.write('\n====== Response End ======\n\n')
        signed_file.close()
        if os.path.getsize(filepath) > 0:
            signed_file = open(filepath, 'r')
            signed_data_content = signed_file.read()
            log.debug('Signed data content:')
            util.display_string(signed_data_content)
            signed_file.close()
        else:
            log.warning('No data in ReSUDI Certificate file')
            return False
    except (IOError, OSError) as e:
        log.warning('Error : {}'.format(e))
        log.warning('Unable to write or read content ReSUDI Certificate.')
        return False
    # -------------------------------------------------------------------------------------

    blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs)
    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'tftp -g -r signed_data_{}.txt {}\r'.format(sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='signed_data_{}.txt'.format(sn),
            prompt='IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    return result


def blade_get_cert_chain(conn, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Get Cert Chain

    As TDE, need a function to request for CertChain on a Blade

    :param conn: UUT connection
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - sn: UUT's serial number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return True or False
    """
    userdict = lib.apdicts.userdict
    result = True

    sn = kwargs['sn']
    server_ip = kwargs['server']

    if re.search('.*{}.*'.format(sn), conn.recbuf):
        util.send(conn, 'rm *{}*\r'.format(sn), 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)

    exit_to_host(conn=conn)

    util.send(conn, 'cd /tftpboot\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'ls -la | grep "{}"\r'.format(sn), 'gen-apollo@.*$', timeout=timeout, regex=True)
    if re.search('.*{}.*'.format(sn), conn.recbuf):
        util.send(conn, 'rm *{}*\r'.format(sn), 'gen-apollo@.*$', timeout=timeout, regex=True)

    # Get Cert Chain
    # -----CESIUMLIB-----
    def __get_act2_certificate_chain():
        return cesiumlib.get_act2_certificate_chain()

    log.debug('INSIDE LOGIN MFG ACT2')
    log.info('---------------------------------------------')
    log.info('Calling cesium library to get the certificate chain')
    try:
        act2_certificate_chain = __get_act2_certificate_chain()
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False
    else:
        log.info('Successfully executed certificate chain')
        log.info('---------------------------------------------')
        cert_chain_data = act2_certificate_chain[0]
        cert_chain_data_len = act2_certificate_chain[1]
        log.debug('Cert Chain Data Len Expected: {}'.format(cert_chain_data_len))
        log.debug('Cert Chain Data Len Recieved: {}'.format(len(cert_chain_data) / 2))
        log.debug('Cert Chain Data:')
        util.display_string(cert_chain_data)

        if int(cert_chain_data_len) != len(cert_chain_data) / 2:
            log.warning('Length of the recieved certificate is incorrect. \
                         Expected: {}, Recieved; {}'.format(cert_chain_data_len, len(cert_chain_data) / 2))
            return False
    # Gen File my_cert_chain_{}.txt
    try:
        filepath = os.path.join('/tftpboot', 'my_cert_chain_{}.txt'.format(sn))
        cert_file = open(filepath, 'a+')
        os.chmod(filepath, 0o777)
        cert_file.write('\n\nResponse Status: SUCCESS\n\n\n====== Response Begin ======\n\n')
        cert_file.write('MUACCertChainLength={}\n'.format(cert_chain_data_len))
        cert_file.write('MUACCertificateChain={}\n'.format(cert_chain_data))
        cert_file.write('\n====== Response End ======\n\n')
        cert_file.close()
        if os.path.getsize(filepath) > 0:
            cert_file = open(filepath, 'r')
            my_cert_chain_content = cert_file.read()
            log.debug('Cert Chain content:')
            util.display_string(my_cert_chain_content)
            cert_file.close()
        else:
            log.warning('No data in CERT Chain file')
            return False
    except (IOError, OSError) as e:
        log.warning('Error : {}'.format(e))
        log.warning('Unable to write or read content Cert chain.')
        return False
    # ---------------------------------------------------------------------------------------------------

    if not util.check_file_exists(
            conn=conn,
            filename='my_cert_chain_{}.txt'.format(sn),
            prompt='gen-apollo@.*$',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    util.send(conn, '\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
    blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs)

    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'tftp -g -r my_cert_chain_{}.txt {}\r'.format(sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='my_cert_chain_{}.txt'.format(sn),
            prompt='IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    return result


def blade_get_session_id(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Get Session ID
    As TDE, need a function to get Session ID for a Blade
    :param conn: UUT's connection
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - sn: UUT's Serial Number
            - bin_image: Binary image name for ACT2 certificate installation
    :return True or False
    """
    log.info('-----Get Session ID for Step 2 Login-----')
    userdict = lib.apdicts.userdict
    result = True

    sn = kwargs['sn']
    image = kwargs['bin_image']

    # Login for Step 2
    util.send(conn, '/tmp/{} --action tam-mfg-login-step-2 --tam-chip-id 0 '.format(image) +
              '--tam-login-signature signed_data_{}.txt\r'.format(sn),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    userdict['session_id'] = ''

    tam_response = conn.recbuf
    if not util.response_success(tam_response):
        log.error('Mfg Login Status Not Found')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    for tam_line in tam_response.splitlines():
        if 'Session ID' in tam_line:
            userdict['session_id'] = tam_line.split('=')[1].strip()
            break

    if userdict['session_id'] == '':
        log.error('Couldnt get session id from recbuf\n{}'.format(tam_response))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    log.info('Session ID: {}'.format(userdict['session_id']))

    util.send(conn, 'exit\r', expectphrase, timeout=timeout)
    result = exit_to_host(conn=conn)

    return result


def blade_install_cliip(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Install CLIIP
    As TDE, need a function to install CLIIP to a Blade
    :param conn: UUT's connection
    :expectphrase: UUT's diag prompt
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - sn: UUT's Serial Number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server's IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return True or False
    """
    log.info('-----Install CLIIP-----')
    userdict = lib.apdicts.userdict
    session_id = userdict['session_id']
    result = True

    sn = kwargs['sn']
    image = kwargs['bin_image']
    server_ip = kwargs['server']

    # Get CLIIP
    # -----CESIUMLIB-----
    result, act2_cliip = get_cliip_act2(userdict['chip_sn'])
    act2_cliip_data_len = act2_cliip[1]
    act2_cliip_data = act2_cliip[0]
    log.debug('ACT2 CLIIP Data: ')
    util.display_string(act2_cliip_data)
    log.debug('ACT2 CLIIP Data Length Expected: {}'.format(act2_cliip_data_len))
    log.debug('ACT2 CLIIP Data Length Recieved: {}'.format(len(act2_cliip_data) / 2))

    if int(act2_cliip_data_len) != (len(act2_cliip_data) / 2):
        log.warning('ACT2 CLIIP Length Mismatch. Expected: {}, Recieved: {}'.format(act2_cliip_data_len,
                                                                                    len(act2_cliip_data) / 2))
        return False
    # Gen cimc_cliip_{}.txt
    try:
        filepath = os.path.join('/tftpboot', 'cimc_cliip_{}.txt'.format(sn))
        cimc_file = open(filepath, 'a+')
        os.chmod(filepath, 0o777)
        cimc_file.write('\n\nResponse Status: SUCCESS\n\n\n====== Response Begin ======\n\n')
        cimc_file.write('CliipDataLen={}\n'.format(act2_cliip_data_len))
        cimc_file.write('CliipData={}\n'.format(act2_cliip_data))
        cimc_file.write('\n====== Response End ======\n\n')
        cimc_file.close()
        if os.path.getsize(filepath) > 0:
            cimc_file = open(filepath, 'r')
            cimc_cliip_content = cimc_file.read()
            log.debug('cimc cliip content:')
            util.display_string(cimc_cliip_content)
            cimc_file.close()
        else:
            log.warning('No data in CIMC CLIIP file')
            return False
    except (IOError, OSError) as e:
        log.warning('Error : {}'.format(e))
        log.warning('Unable to write or read content CIMC CLIIP.')
        return False
    # ---------------------------------------------------------------------------------------------

    result = blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs)

    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'tftp -g -r cimc_cliip_{}.txt {}\r'.format(sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='cimc_cliip_{}.txt'.format(sn),
            prompt='IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    # Install CLIIP to Chip
    util.send(conn, '/tmp/{} --action tam-install-cliip '.format(image) +
              '--tam-cliip cimc_cliip_{}.txt --tam-chip-id 0 --tam-session-id {}\r'.format(sn, session_id),
              'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.sleep(10)
    # Handle in case CLIIP is already installed, continue
    if 'TAM Chip 0 CLIIP Installation Status = 0x1' in conn.recbuf:
        log.error('CLIIP already installed.')
    elif not util.response_success(conn.recbuf):
        log.error('Install CLIIP Status Not Found')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False
    log.info('ACT2 CLIIP Status Inserted')

    util.send(conn, 'exit\r', expectphrase, timeout=timeout)
    result = exit_to_host(conn=conn)

    # Record CLIIP Insertion Status
    result = record_act2_cliip_insertion_status(userdict['chip_sn'], 6)

    if not result:
        log.error('Error inserting CLIIP Status')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    log.info('ACT2 CLIIP Status Inserted and Recorded')

    return result


def blade_install_sudi(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Install SUDI
    As TDE, need a function to install SUDI to a Blade
    :param conn: UUt's connection
    :param expectphrase: UUT's diag prompt
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - cert_type: Type of SUDI to be Installed (RSA or ECC or HARSA)
            - sn: UUT's Serial Number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server's IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    session_id = userdict['session_id']
    global resudi

    sn = kwargs['sn']
    cert_type = kwargs['cert_type']
    image = kwargs['bin_image']
    server_ip = kwargs['server']

    log.info('-----Install SUDI {}-----'.format(cert_type.upper()))

    cms_data = get_cms_data(
        conn=conn,
        expectphrase=expectphrase,
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list,
        sudi_or_resudi='sudi',
        session_id=session_id,
        **kwargs
    )
    log.debug('CMS Data: ')
    util.display_string(cms_data)
    if cms_data == '':
        return False

    # Get SUDI Cert
    # -----CESIUMLIB-----
    def __get_act2_sudi_certificate(act2_cms_data):
        return cesiumlib.get_act2_sudi_certificate(act2_cms_data)

    log.info('---------------------------------------------')
    log.info('Calling cesium library to get sudi {} cert'.format(cert_type.upper()))

    try:
        act2_sudi_cert = __get_act2_sudi_certificate(act2_cms_data=cms_data)
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        # ATOM SN not entered into CBE for this PID
        if '13026' in e.message:
            # log.debug('data type: {}'.format(error_message.message))
            log.warning('Error 13026 found.  Token SN not currently in CBE')
            # capture token SN + PID
            token_sn = re.search('(Token with serial \()([a-f0-9]+)(\))', e.message).group(2).strip()
            token_pid = re.search('(PID:)([\d\w-]*)(!)', e.message).group(2).strip()
            log.warning('Token SN: {}'.format(token_sn))
            log.warning('Token PID: {}'.format(token_pid))
        # reSUDI required
        elif '13023' in e.message:
            log.info('Need to ReSUDI.')
            userdict['{}_resudi'.format(cert_type)] = True
            # do not set result to fail.  resudi is needed. this does not mean the unit should fail
            resudi = True
            return True
        else:
            log.warning('Not sure what is wrong.  Failing unit')
            userdict['operator_message'] = util.operator_message(
                error_message='Error:{} {}'.format(cert_type.upper(), util.whoami()),
                resolution_message='Call Support',
            )
            return False
    log.info('Successfully execute sudi {} certificate'.format(cert_type.upper()))
    log.info('---------------------------------------------')

    cert_len = act2_sudi_cert.sudi_cert_len
    cert_data = act2_sudi_cert.sudi_cert
    ca_len = act2_sudi_cert.sudi_ca_cert_len
    root_len = act2_sudi_cert.sudi_root_cert_len
    ca_data = act2_sudi_cert.sudi_ca_cert
    root_data = act2_sudi_cert.sudi_root_cert

    log.debug('Cert Data: ')
    util.display_string(cert_data)
    log.debug('Cert Data Length Expected: {}'.format(cert_len))
    log.debug('Cert Data Length Recieved: {}'.format(len(cert_data) / 2))
    log.debug('CA Data: ')
    util.display_string(ca_data)
    log.debug('CA Data Length Expected: {}'.format(ca_len))
    log.debug('CA Data Length Recieved: {}'.format(len(ca_data) / 2))
    log.debug('Root Data: ')
    util.display_string(root_data)
    log.debug('Root Data Length Expected: {}'.format(root_len))
    log.debug('Root Data Length Recieved: {}'.format(len(root_data) / 2))

    if (int(cert_len) != len(cert_data) / 2) or (int(ca_len) != len(ca_data) / 2) or (int(root_len) != len(root_data) / 2):
        log.warning('SUDI Ceriticate Length Mismatch.')
        return False

    # Gen File my_sudi_certificate_{}.txt
    try:
        filepath = os.path.join('/tftpboot', 'my_sudi_{}_certificate_{}.txt'.format(cert_type, sn))
        sudi_file = open(filepath, 'a+')
        os.chmod(filepath, 0o777)
        sudi_file.write('SudiCertificate={}\n'.format(cert_data))
        sudi_file.write('SudiCertificateLen={}\n'.format(cert_len))
        sudi_file.write('SudiCACert={}\n'.format(ca_data))
        sudi_file.write('SudiCACertLen={}\n'.format(ca_len))
        sudi_file.write('SudiRootCert={}\n'.format(root_data))
        sudi_file.write('SudiRootCertLen={}\n'.format(root_len))
        sudi_file.close()
        if os.path.getsize(filepath) > 0:
            sudi_file = open(filepath, 'r')
            sudi_cert_content = sudi_file.read()
            log.debug('sudi_cert_content:')
            util.display_string(sudi_cert_content)
            sudi_file.close()
        else:
            log.warning('No data in SUDI Certificte file')
            return False
    except (IOError, OSError) as e:
        log.warning('Error : {}'.format(e))
        log.warning('Unable to write or read content SUDI Certificte.')
        return False

    if not blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return False

    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'tftp -g -r my_sudi_{}_certificate_{}.txt {}\r'.format(cert_type, sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='my_sudi_{}_certificate_{}.txt'.format(cert_type, sn),
            prompt='IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error:{}-{}'.format(cert_type.upper(), util.whoami()),
            resolution_message='Call Support',
        )
        return False

    # Install SUDI to Chip
    util.send(conn, '/tmp/{} --action tam-install-sudi-certificates '.format(image) +
              '--device-cert /tmp/my_sudi_{}_certificate_{}.txt --tam-chip-id 0 '.format(cert_type, sn) +
              '--tam-session-id {} --tam-certificate-type {}\r'.format(session_id, cert_type.upper()),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if 'Successfully installed' not in conn.recbuf:
        log.error('Error installing sudi cert {}'.format(cert_type.upper()))
        log.debug('Recbuf: {}'.format(conn.recbuf))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}-{}'.format(cert_type.upper(), util.whoami()),
            resolution_message='Call Support',
        )
        return False
    else:
        log.info('Sudi Cert {} Successfully Installed'.format(cert_type.upper()))

    util.send(conn, 'exit\r', expectphrase, timeout=timeout)
    result = exit_to_host(conn=conn)

    log.info('ACT2 SUDI {} Installed'.format(cert_type.upper()))

    return result


def blade_install_resudi(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Install RESUDI
    As TDE, need a function to install RESUDI to a Blade
    :param conn: UUT's connection
    :param expectphrase: UUT's diag prompt
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - cert_type: Type of SUDI to be Installed (RSA or ECC or HARSA)
            - sn: UUT's Serial Number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server's IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return: True or False
    """

    userdict = lib.apdicts.userdict
    session_id = userdict['session_id']

    sn = kwargs['sn']
    cert_type = kwargs['cert_type']
    image = kwargs['bin_image']
    server_ip = kwargs['server']

    log.info('-----Install RESUDI {}-----'.format(cert_type.upper()))
    cms_data = get_cms_data(
        conn=conn,
        expectphrase=expectphrase,
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list,
        sudi_or_resudi='resudi',
        session_id=session_id,
        **kwargs
    )
    log.debug('CMS Data: ')
    util.display_string(cms_data)
    if cms_data == '':
        return False

    # Get RESUDI Cert
    # -----CESIUMLIB-----
    def __get_act2_resudi_certificate(act2_cms_data):
        return cesiumlib.get_act2_resudi_certificate(act2_cms_data)

    log.info('---------------------------------------------')
    log.info('Calling cesium library to get sudi {} cert'.format(cert_type.upper()))

    try:
        act2_sudi_cert = __get_act2_resudi_certificate(act2_cms_data=cms_data)
    except apexceptions.ServiceFailure as e:
        log.warning('Service Failure found: {}'.format(e))
        log.info('---------------------------------------------')
        # ATOM SN not entered into CBE for this PID
        if '13026' in e.message:
            # log.debug('data type: {}'.format(error_message.message))
            log.warning('Error 13026 found.  Token SN not currently in CBE')
            # capture token SN + PID
            token_sn = re.search('(Token with serial \()([a-f0-9]+)(\))', e.message).group(2).strip()
            token_pid = re.search('(PID:)([\d\w-]*)(!)', e.message).group(2).strip()
            log.warning('Token SN: {}'.format(token_sn))
            log.warning('Token PID: {}'.format(token_pid))
        else:
            log.warning('Not sure what is wrong.  Failing unit')
            userdict['operator_message'] = util.operator_message(
                error_message='Error:{}-{}'.format(cert_type.upper(), util.whoami()),
                resolution_message='Call Support',
            )
            return False
    log.info('Successfully execute sudi {} certificate'.format(cert_type.upper()))
    log.info('---------------------------------------------')

    cert_len = act2_sudi_cert.sudi_cert_len
    cert_data = act2_sudi_cert.sudi_cert
    ca_len = act2_sudi_cert.sudi_ca_cert_len
    root_len = act2_sudi_cert.sudi_root_cert_len
    ca_data = act2_sudi_cert.sudi_ca_cert
    root_data = act2_sudi_cert.sudi_root_cert

    log.debug('Cert Data: ')
    util.display_string(cert_data)
    log.debug('Cert Data Length Expected: {}'.format(cert_len))
    log.debug('Cert Data Length Recieved: {}'.format(len(cert_data) / 2))
    log.debug('CA Data: ')
    util.display_string(ca_data)
    log.debug('CA Data Length Expected: {}'.format(ca_len))
    log.debug('CA Data Length Recieved: {}'.format(len(ca_data) / 2))
    log.debug('Root Data: ')
    util.display_string(root_data)
    log.debug('Root Data Length Expected: {}'.format(root_len))
    log.debug('Root Data Length Recieved: {}'.format(len(root_data) / 2))

    if (int(cert_len) != len(cert_data) / 2) or (int(ca_len) != len(ca_data) / 2) or (int(root_len) != len(root_data) / 2):
        log.warning('RESUDI Certificate Length Mismatch.')
        return False

    # Gen File my_sudi_certificate_{}.txt
    try:
        filepath = os.path.join('/tftpboot', 'my_resudi_{}_certificate_{}.txt'.format(cert_type, sn))
        resudi_file = open(filepath, 'a+')
        os.chmod(filepath, 0o777)
        resudi_file.write('SudiCertificate={}\n'.format(cert_data))
        resudi_file.write('SudiCertificateLen={}\n'.format(cert_len))
        resudi_file.write('SudiCACert={}\n'.format(ca_data))
        resudi_file.write('SudiCACertLen={}\n'.format(ca_len))
        resudi_file.write('SudiRootCert={}\n'.format(root_data))
        resudi_file.write('SudiRootCertLen={}\n'.format(root_len))
        resudi_file.close()
        if os.path.getsize(filepath) > 0:
            resudi_file = open(filepath, 'r')
            resudi_cert_content = resudi_file.read()
            log.debug('ReSUDI cert content:')
            util.display_string(resudi_cert_content)
            resudi_file.close()
        else:
            log.warning('No data in ReSUDI Certificte file')
            return False
    except (IOError, OSError) as e:
        log.warning('Error : {}'.format(e))
        log.warning('Unable to write or read content RESUDI Ceriticate.')
        return False

    if not blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return False

    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    util.send(conn, 'tftp -g -r my_resudi_{}_certificate_{}.txt {}\r'.format(cert_type, sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if not util.check_file_exists(
            conn=conn,
            filename='my_resudi_{}_certificate_{}.txt'.format(cert_type, sn),
            prompt='IBMC-SLOT\[.*\] #',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}-{}'.format(cert_type.upper(), util.whoami()),
            resolution_message='Call Support',
        )
        return False

    # Install ReSUDI to Chip
    util.send(conn, '/tmp/{} --action tam-install-sudi-certificates '.format(image) +
              '--device-cert /tmp/my_resudi_{}_certificate_{}.txt --tam-chip-id 0 '.format(cert_type, sn) +
              '--tam-session-id {} --tam-certificate-type {}\r'.format(session_id, cert_type.upper()),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if 'Successfully installed' not in conn.recbuf:
        log.error('Error installing sudi cert {}'.format(cert_type.upper()))
        log.debug('Recbuf: {}'.format(conn.recbuf))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}-{}'.format(cert_type.upper(), util.whoami()),
            resolution_message='Call Support',
        )
        return False
    else:
        log.info('RESudi Cert {} Successfully Installed'.format(cert_type.upper()))

    util.send(conn, 'exit\r', expectphrase=expectphrase, timeout=timeout)
    result = exit_to_host(conn=conn)

    log.info('ACT2 RESUDI {} Installed'.format(cert_type.upper()))

    return result


def get_cms_data(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Get CMS Data

    Get CMS data for SUDI and Resudi

    :param conn:
    :param expectphrase:
    :param timeout:
    :param skip_fail_pars_list:
    :param kwargs: It must contain following arguments:
            - sudi_or_resudi: Cert to Request ('sudi' or 'resudi')
            - session_id: Session ID of ACT2 Mfg Login
            - cert_type: Type of SUDI to be Installed (RSA or ECC or HARSA)
            - sn: UUT's Serial Number
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
            - server: Server's IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : username used to login to server
                - password: password used to login to server
    :return: cms_data (String) empty if error
    """
    userdict = lib.apdicts.userdict

    sudi_or_resudi = kwargs['sudi_or_resudi']
    session_id = kwargs['session_id']
    sn = kwargs['sn']
    cert_type = kwargs['cert_type']
    image = kwargs['bin_image']
    server_ip = kwargs['server']

    if not blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs):
        return ''

    util.send(conn, 'cd /tmp\r', 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        return ''

    # Request Cert
    util.send(conn, '/tmp/{} --action tam-generate-sudi --tam-chip-id 0 '.format(image) +
              '--tam-session-id {} '.format(session_id) +
              '--tam-out-file my_{}_{}_request_{}.txt '.format(sudi_or_resudi, cert_type, sn) +
              '--tam-certificate-type {}\r'.format(cert_type.upper()), 'IBMC-SLOT\[.*\] #',
              timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        return ''

    log.info('TAM cert {} response:\n{}'.format(cert_type.upper(), conn.recbuf))

    util.send(conn, 'tftp -r /my_{}_{}_request_{}.txt -p {}\r'.format(sudi_or_resudi, cert_type, sn, server_ip),
              'IBMC-SLOT\[.*\] #',
              timeout=timeout,
              regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        return ''

    util.send(conn, 'exit\r', expectphrase=expectphrase, timeout=timeout)

    if not exit_to_host(conn=conn):
        return ''

    util.send(conn, 'cd /tftpboot\r', 'gen-apollo@.*$', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        return ''

    if not util.check_file_exists(
            conn=conn,
            filename='my_{}_{}_request_{}.txt'.format(sudi_or_resudi, cert_type, sn),
            prompt='gen-apollo@.*$',
            timeout=timeout,
            regex=True
    ):
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return ''

    util.send(conn, 'cat my_{}_{}_request_{}.txt\r'.format(sudi_or_resudi, cert_type, sn),
              'gen-apollo@.*$', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        return ''

    sudi_request_dict = util.parse_for_key_value_pair(buffer=conn.recbuf, delimiter='=')

    return sudi_request_dict['SudiRequestHexBytes']


def blade_verify_certificates(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ ACT2 Verify Certificates
    As TDE, need a function to Check ACT2 Certificates once it was installed for the very first time
    :param conn: UUt's connection
    :param expectphrase: UUT's diag prompt
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: It must contain following arguments:
            - bin_image: Binary image name for ACT2 certificate installation
            - mio_ip_suffix: UUT's MIO IP suffix
            - blade_ip_suffix: UUT's Blade IP suffix
    :return: True or False
    """
    log.info('-----Verifying Certifictes Installation-----')
    userdict = lib.apdicts.userdict
    session_id = userdict['session_id']
    result = True

    image = kwargs['bin_image']

    result = blade_connect(conn=conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs)

    util.send(conn, '/tmp/{} --action tam-verify-certificates --tam-chip-id 0 '.format(image) +
              '--tam-session-id {}\r'.format(session_id), 'IBMC-SLOT\[.*\] #', timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    cert_verification_response = conn.recbuf
    util.send(conn, 'exit\r', expectphrase, timeout=timeout)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        log.warning('Error phrase found')
        result = False

    if 'All required certificates passed authentication on TAM chip 0' not in cert_verification_response:
        log.error('There have been an error on certs installation')
        log.debug('Recbuf:\n{}'.format(cert_verification_response))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    log.info('ACT2 Certs installed Successfully')

    return result


def blade_mcclient(conn, expectphrase=prompt, timeout=200, retry=1, skip_fail_pars_list=False, **kwargs):
    """ ACT2 Necessary
    As TDE, need a function to perform all MCClient Process before an ACT2 installation was done

    :param conn: UUT's connection
    :param expectphrase: UUT's diag prompt
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs:
            - sn: UUT's Serial Number
            - module_no: UUT's Blade slot number
            - mio_ip_suffix: UUT's MIO IP suffix
            - server: Server's IP
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
    :return: True or False
    """
    log.info('-----MCClient-----')
    userdict = lib.apdicts.userdict
    result = True

    sn = kwargs['sn']
    blade_slot = kwargs['module_no']

    try:
        util.send(conn, '\r', expectphrase, timeout=timeout)
        util.send(conn, 'cd /mio/bks/bin\r', expectphrase, timeout=timeout)
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            log.warning('Error phrase found')
            result = False

        util.send(conn, 'ping 127.3.0.{} -c5\r'.format(blade_slot),
                  '--- 127.3.0.{} ping statistics ---'.format(blade_slot), timeout=timeout)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False
        util.sleep(10)

        if '0% packet loss' not in conn.recbuf:
            log.error('Cannot ping to 127.3.0.{}'.format(blade_slot))
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {}'.format(util.whoami()),
                resolution_message='Call Support',
            )
            return False

        util.send(conn, './mcclient --ip=127.3.0.{} '.format(blade_slot) +
                  '--setipmiusers=/mio/bks/scripts/MFG-Enable-Users_Sec.txt\r', 'Successful [0]',
                  retry=retry, timeout=timeout)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

        util.sleep(10)
        util.send(conn, '\r', expectphrase, timeout=timeout)
        util.send(conn, './mcclient --ip=127.3.0.{} '.format(blade_slot) +
                  '--setbiostoken=/mio/bks/scripts/consoleredir.xml\r', 'Successful [0]',
                  retry=retry, timeout=timeout)
        util.sleep(10)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

        util.send(conn, '\r', expectphrase, timeout=timeout)

        # Verify again ACT2 Installation
        need_act2, result = blade_verify_act2(conn, timeout=timeout, skip_fail_pars_list=skip_fail_pars_list, **kwargs)
        if not result or need_act2:
            return False

        exit_to_host(conn=conn)
        folders_to_clean = ['', '/tmp/', '/tftpboot/']

        log.info('------Deleting ACT2 generated Files------')
        for folder in folders_to_clean:
            util.send(
                conn,
                'rm -f {}*{}*.txt\r'.format(folder, sn),
                'gen-apollo@.*$',
                timeout=timeout,
                regex=True
            )
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)
                result = False
        log.info('-----ACT2 Generated Files deleted!-----')

    except Exception, e:
        log.error('Catched Error on MCClient: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    log.info('---MCClient Done---')

    result = mio_connect(conn, **kwargs)
    return result


def set_firmware_version(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Set package version for Rommon and FPGA firmware image.
    As TDE, will provide a way to set package version for  bumdle Rommon & FPGA firmware
    :param conn: UUT's connection
    :param timeout: Wait time in seconds
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required:
            - rommon_ver:  rommon version
            - fpga_ver: fpga version
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    rommon_ver = kwargs['rommon_ver']
    fpga_ver = kwargs['fpga_ver']
    test_name = lib.getstepdata()['stepdict']['name']
    result = False

    test_command = 'diag mio utils upgrade bundle verrom-v {} verfpga-V {}'.format(rommon_ver, fpga_ver)
    result = run_functional_test(conn=conn,
                                 test_name=test_name,
                                 test_command=test_command,
                                 timeout=timeout,
                                 expectphrase=expectphrase,
                                 skip_fail_pars_list=skip_fail_pars_list
                                 )

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update bundle package versionRommon and FPGA'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def verify_firmware_version(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Verify package version for Rommon and FPGA firmware image.
    As TDE, will provide a way to verify package version for  bumdle Rommon & FPGA firmware
    :param conn: UUT's connection
    :param timeout: Wait time in seconds
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required:
            - rommon_ver: expected rommon version
            - fpga_ver: expected fpga version
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    rommon_ver = kwargs['rommon_ver']
    fpga_ver = kwargs['fpga_ver']
    test_name = lib.getstepdata()['stepdict']['name']
    result = False

    test_command = 'diag mio utils verify pkg_ver verrom-v {} verfpga-V {}'.format(rommon_ver, fpga_ver)
    result = run_functional_test(conn=conn,
                                 test_name=test_name,
                                 test_command=test_command,
                                 timeout=timeout,
                                 expectphrase=expectphrase,
                                 skip_fail_pars_list=skip_fail_pars_list
                                 )

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Verify failed bundle Rommon and FPGA package version'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_bundle(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=1000, **kwargs):
    """Update Rommon and FPGA using bundle  firmware image.
    As TDE, will provide a way to upgrade bumdle Rommon & FPGA firmware

    :param timeout: Wait time in seconds
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required:
            - conn: UUT's connection
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: Server's IP
            - destination_path: Path where file will be copied
            - rommon_img:  rommon binary image
            - fpga_img: fpga binary image
            - rommon_prompt: Rommon's prompt
    :return: True or False
    """

    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    rommon_img = kwargs['rommon_img'] if 'rommon_img' in kwargs else None
    rommon_ver = kwargs['rommon_ver'] if 'rommon_ver' in kwargs else None
    fpga_img = kwargs['fpga_img'] if 'fpga_img' in kwargs else None
    fpga_ver = kwargs['fpga_ver'] if 'fpga_ver' in kwargs else None
    rommon_prompt = kwargs['rommon_prompt']

    userdict = lib.apdicts.userdict
    result = False
    source_path = 'tftpboot'

    # upgrade command
    upgrade_cmd = 'diag mio utils upgrade bundle'
    # Build command
    if rommon_img and rommon_ver:
        result = True
        upgrade_cmd += ' fwrom-f {} verrom-v {}'.format(rommon_img, rommon_ver)
    if fpga_img and fpga_ver:
        result = True
        upgrade_cmd += ' fwfpga-F {} verfpga-V {}'.format(fpga_img, fpga_ver)
    log.debug('Upgrade command: {}'.format(upgrade_cmd))
    if result:
        # Copy Rommon Image
        copy_rommon_image = util.scp(
            conn=conn,
            username=username,
            password=password,
            source_server=source_server,
            source_path=source_path,
            destination_path=destination_path,
            file=rommon_img,
            prompt=expectphrase
        )
        # Copy FPGA Image
        copy_fpga_image = util.scp(
            conn=conn,
            username=username,
            password=password,
            source_server=source_server,
            source_path=source_path,
            destination_path=destination_path,
            file=fpga_img,
            prompt=expectphrase
        )

        if copy_rommon_image and copy_fpga_image:
            util.sende(conn, '{}\r'.format(upgrade_cmd), rommon_prompt, timeout=timeout, regex=True)
            util.sleep(30)
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)
                result = False

            if result:
                util.sende(conn, '\r', rommon_prompt, timeout=timeout, regex=True)
        else:
            log.warning('Rommon or FPGA Image not found!')
            result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update bundle Rommon and FPGA'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_rommon(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Update Rommon.
    As TDE, will provide a way to upgrade Rommon firmware

    :param timeout: Wait time in seconds
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required:
            - conn: UUT's connection
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: Server's IP
            - destination_path: Path where file will be copied
            - rommon_img: Rommon binary image
            - rommon_prompt: Rommon's prompt
    :return: True or False
    """

    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    rommon_img = kwargs['rommon_img']
    rommon_prompt = kwargs['rommon_prompt']

    userdict = lib.apdicts.userdict
    result = True
    source_path = 'tftpboot'

    # Copy Rommon Image
    copy_image = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=rommon_img,
        prompt=expectphrase
    )

    if copy_image:
        test_command = 'diag mio utils upgrade rommon filename {}\r'.format(rommon_img)
        util.sende(conn, test_command, rommon_prompt, timeout=timeout, regex=True)
        util.sleep(100)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

        if result:
            util.sende(conn, '\r', rommon_prompt, timeout=timeout, regex=True)
    else:
        log.warning('Rommon Upgrade Image not found!')
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update Rommon'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_fpga(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Update FPGA.
    As TDE, will provide a way to upgrade FPGA firmware

    :param conn: UUT's connection
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Ignore any error/Fail message if True
    :param timeout: Wait time in seconds
    :param kwargs: Required:
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: Server's IP
            - destination_path: Path where the file will be copied
            - fpga_gold_img: FPGA binary image
            - fpga_upgrade_img: FPGA upgrade image
    :return: True or False
    """
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    fpga_gold_img = kwargs['fpga_gold_img']
    fpga_upgrade_img = kwargs['fpga_upgrade_img']

    userdict = lib.apdicts.userdict
    result = True
    source_path = 'tftpboot'

    # Copy FPGA Image
    copy_gold_image = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=fpga_gold_img,
        prompt=expectphrase
    )

    copy_upgrade_image = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=fpga_upgrade_img,
        prompt=expectphrase
    )
    # Navigate to destination path
    util.send(conn,
              text='cd {}\r'.format(destination_path),
              expectphrase=prompt,
              timeout=timeout)
    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False
    try:
        if copy_upgrade_image and copy_gold_image:
            command_list = [
                ('pbrfpga -g {}\r'.format(fpga_gold_img), ['Finish golden FPGA upgrade!'], timeout),
                ('pbrfpga -u {}\r'.format(fpga_upgrade_img), ['Finish upgrade region of FPGA!'], timeout)
            ]

            util.send_commands(conn, command_list)
    except Exception, e:
        log.warning('{}'.format(e))

        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False
    else:
        log.warning('FPGA Image not found!')
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update FPGA'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_pseq(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Update pseq.
    As TDE, will provide a way to upgrade pseq firmware

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Is the list variable to skip each fail for the position list in the parsing result
        The values are (True or False), True is for skip, and False is for don't skip the failure
    :param timeout: Is the time out variable to be used inside the sende instructions
    :param kwargs: Required:
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: This is the ip images server
            - destination_path: This is the destionation path to be stored the files
            - img: This are the list of the legacy files pseq update
            - mvimg: This is the list of the new name to rename the files in the img list, this is need because
                menush use this static names to execute the update
    :return: True if Pass, False instead
    """

    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    img = kwargs['img']
    mvimg = kwargs['mvimg']

    userdict = lib.apdicts.userdict
    result = True
    source_path = 'tftpboot'

    if not img:
        img = []
    if not mvimg:
        mvimg = []

    # Copy pseq Images
    copy_image1 = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=img[0],
        prompt=expectphrase
    )

    copy_image2 = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=img[1],
        prompt=expectphrase
    )

    # Validate both files were copy
    if copy_image1 and copy_image2:
        # rename the file img 0
        mv_image1 = util.move(conn, destination_path, img[0], mvimg[0], prompt=expectphrase, regex=True)
        # rename the file img 1
        mv_image2 = util.move(conn, destination_path, img[1], mvimg[1], prompt=expectphrase, regex=True)
        # Validate both files were copy
        if mv_image1 and mv_image2:
            # Run the upgrade pseq
            util.sende(conn,
                       'diag mio utils upgrade pseq-bridge\r',
                       expectphrase=['Found phrase [Successfully upgraded the PSEQ firmware].',
                                     'Cisco System ROMMON, Version', expectphrase],
                       timeout=timeout,
                       regex=True)
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)
                result = False
        else:
            log.warning('PSEQ Upgrade Image cannot be moved!')
            result = False
    # Catch if the file copied was not successful
    else:
        log.warning('PSEQ Upgrade Image not found!')
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update PSEQ'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_fpga_basin(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Update pseq.
    As TDE, will provide a way to upgrade fpga firmware to the basin

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Is the list variable to skip each fail for the position list in the parsing result
        The values are (True or False), True is for skip, and False is for don't skip the failure
    :param timeout: Is the time out variable to be used inside the sende instructions
    :param kwargs: Required:
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: This is the ip images server
            - destination_path: This is the destination path to be stored the files
            - img: This are the list of the legacy files fpga update
    :return: True if Pass, False instead
    """

    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    img = kwargs['img']

    userdict = lib.apdicts.userdict
    result = True
    source_path = 'tftpboot'

    # Copy pseq Image
    copy_image = util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=img,
        timeout=600,
        prompt=expectphrase
    )

    if copy_image:
        util.sende(conn,
                   'diag mio utils upgrade basin_fpga filename {}\r'.format(img),
                   expectphrase=['Golden FPGA upgrade Done!'],
                   timeout=timeout,
                   regex=True)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False

    else:
        log.warning('fpga basin Upgrade Image not found!')
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update fpga basin'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_pseq_basin(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=200, **kwargs):
    """Update pseq.
    As TDE, will provide a way to upgrade pseq firmware

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param skip_fail_pars_list: Is the list variable to skip each fail for the position list in the parsing result
        The values are (True or False), True is for skip, and False is for don't skip the failure
    :param timeout: Is the time out variable to be used inside the sende instructions
    :param kwargs: Required:
            - img: This are the list of the legacy files pseq update
            - mvimg: This are the list of the renamed legacy files
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - source_server: This is the ip images server
            - destination_path: This is the destination path to be stored the files
    :return: (String)This return the general result string Pass or Fail
    """
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    img = kwargs['img']
    mvimg = kwargs['mvimg']

    userdict = lib.apdicts.userdict
    result = True
    source_path = 'tftpboot'
    if not img:
        img = []
    if not mvimg:
        mvimg = []

    # Copy pseq Images
    copy_image1 = util.scp(
        conn,
        username,
        password,
        source_server,
        source_path,
        destination_path,
        img[0],
        expectphrase
    )
    copy_image2 = util.scp(
        conn,
        username,
        password,
        source_server,
        source_path,
        destination_path,
        img[1],
        expectphrase
    )

    # Validate the copy was successful
    if copy_image1 and copy_image2:
        # rename the file img 0
        mv_image1 = util.move(conn, destination_path, img[0], mvimg[0], prompt=expectphrase, regex=True)
        # rename the file img 1
        mv_image2 = util.move(conn, destination_path, img[1], mvimg[1], prompt=expectphrase, regex=True)
        # Validate both files were copy
        if mv_image1 and mv_image2:
            # Choose the image based on current PSEQ
            util.sende(conn, 'i2c 2.12 -r1 -o 0x8C0C', expectphrase=expectphrase, timeout=timeout)
            upg_img = mv_image2 if re.search('^01$', conn.recbuf) else mv_image1

            # Run the upgrade pseq
            util.sende(conn,
                       'diag mio utils upgrade basin_app filename {}\r'.format(upg_img),
                       expectphrase=['Upgrade done.'],
                       timeout=timeout,
                       regex=True)
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)
                result = False
    # Catch if the file copied was not successful
    else:
        log.warning('pseq Upgrade Image not found!')
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Update pseq'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def get_ssd_info(conn, retry=0, timeout=200, skip_fail_pars_list=False, **kwargs):
    """ Get SSDs Info .
    :param conn: UUT's connection
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required-
                - disk_list: List of ssd devices
    :return dict with Serial Number, Model Number and Firmware version
    """
    disk_list = kwargs['disk_list']
    ssd_info = {disk: {} for disk in disk_list}
    try:
        for ssd in disk_list:
            log.info('--------------------------')
            log.info('Disk: /dev/{}'.format(ssd))
            # Capture  Serial Number
            util.sende(conn,
                       text="hdparm -I /dev/{} | grep 'Serial Number'\r".format(ssd),
                       expectphrase='Serial Number:(.*)',
                       timeout=timeout,
                       retry=retry,
                       regex=True
                       )
            ssd_info[ssd]['Serial Number'] = re.match('(.*\n.*)Serial Number:(.*)',
                                                      conn.recbuf).group(2).strip()
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)

            log.info('Serial Number: {}'.format(ssd_info[ssd]['Serial Number']))
            # Capture Model Number
            util.sende(conn,
                       text="hdparm -I /dev/{} | grep 'Model Number'\r".format(ssd),
                       expectphrase='Model Number:(.*)',
                       timeout=timeout,
                       retry=retry,
                       regex=True
                       )
            ssd_info[ssd]['Model Number'] = re.match('(.*\n.*)Model Number:(.*)',
                                                     conn.recbuf).group(2).strip()
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)

            log.info('Model Number: {}'.format(ssd_info[ssd]['Model Number']))
            # Capture Firmware Revision
            util.sende(conn,
                       text="hdparm -I /dev/{} | grep 'Firmware Revision'\r".format(ssd),
                       expectphrase='Firmware Revision:(.*)',
                       timeout=timeout,
                       retry=retry,
                       regex=True
                       )
            ssd_info[ssd]['Firmware Revision'] = re.match('(.*\n.*)Firmware Revision:(.*)',
                                                          conn.recbuf).group(2).strip()
            # Check for parsing after send
            if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
                error_message = 'Error phrase found'
                log.warning(error_message)

            log.info('Firmware Revision: {}'.format(ssd_info[ssd]['Firmware Revision']))
            log.info('--------------------------')
    except Exception as e:
        ssd_info = {disk: {} for disk in disk_list}
        log.warning('Error: {} - Unable to parse SSD info '.format(e))

    return ssd_info


def get_disk_size(conn, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Get SSDs Size Capacity.
    As TDE, will provide to display SSD size
    :param conn: UUT's connection object
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param kwargs: Required-
                - disk_list: List of ssd devices
    :return List of disks size
    """
    disk_list = kwargs['disk_list']
    size_list = {disk: {} for disk in disk_list}

    for disk in disk_list:
        util.sende(conn,
                   text='fdisk -ul | grep /dev/{}\r'.format(disk),
                   timeout=timeout,
                   expectphrase=prompt)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)

        if '/dev/{}'.format(disk) in conn.recbuf:
            # Parse disk size
            disk_size = re.search(':\s(\d*\.\d*)\sGB', conn.recbuf).group(1)
            log.info('Disk {} Size: {}'.format(disk, disk_size))
            size_list[disk] = int(float(disk_size))
        else:
            # Reset ssd_size
            size_list = {disk: {} for disk in disk_list}
            log.info('Disk {} not found.'.format(disk))

    return size_list


def test_result_filter(rec_buf_str):
    """
    Remove the Log at the end of the test result. Use this function in conjunction with functional_test
    For example:
    [2.1.2.0] pad# diag blade2 test bmc dimmchannel
    INFO: Shortcut command:  bladebmcdimmslot 2
    INFO: Blade PID: FPR9K-SM-48
    ================================================================
    INFO: Checking DIMM slot placement will take at least 2 mins.

    INFO: bladebmcdimmslot passed.
    CONCLUSION: PASSED
    Log in  /tmp/slot2getbladepid_xH7cIJ /tmp/slot2bladebmcdimmslot_Err3Tx /tmp/slot2bladebmcdimmslot_pAEGQG
    [2.1.2.0] pad#

    Will filter out the "Log in" line from the output. for failure, there is additional "LOG" line

    The purpose is to remove sometimes possible "ERR", "Err" string that shows up in the Log filename. Like
    slot2bladebmcdimmslot_Err3Tx. This will cause the failure
    :param rec_buf_str: input rec_buf string
    :return filtered_buf: Return the test result without the log
    """
    temp_list = []
    temp_rec_buf = rec_buf_str.split('\n')

    for line in temp_rec_buf:
        if 'Log in' not in line and 'LOG' not in line:
            temp_list.append(line)
    filtered_rec_buf = '\n'.join([x for x in temp_list])
    return filtered_rec_buf


def run_functional_test(conn, expectphrase=prompt, retry=0, timeout=1800, skip_fail_pars_list=False, **kwargs):
    """Generic Functional test_name
    As TDE,will te run_functional_test will run any functional test

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param retry: number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/message if True
    :param kwargs: Required:
                    hardware_check: Flag to trigger a question to check if the hardware is present physically
                                    before failing if the test follows INFO/CONCLUSION format. Default set to False
                                    For example, Check SSD is fully inserted.
                    test_name: Name of the test to perform
                    test_command: Test's Command to perform
    :return: True is PASS, False instead
    """
    test_name = kwargs['test_name']
    userdict = lib.apdicts.userdict

    result, must_validate = send_cmd(conn, expectphrase, timeout, retry, **kwargs)

    # Filter out the log filenames at the end of the test result
    temp_rec_buf = test_result_filter(conn.recbuf)

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(temp_rec_buf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Run Functional Test'.format(util.whoami()),
            resolution_message='Call support',
        )
    if must_validate:
        log.info(' {}.....[RESULT]'.format(test_name))
        return True
    elif result:
        log.info(' {}.....[PASSED]'.format(test_name))
        return True
    else:
        log.info(' {}.....[FAILED]'.format(test_name))
        return False


def send_cmd(conn, expectphrase, timeout=1800, retry=0, **kwargs):
    """Send CMD

    Send test command and evaluate buffer and hardware check

    :param conn:
    :param expectphrase:
    :param timeout:
    :param retry:
    :param kwargs: Required:
                    hardware_check: Flag to trigger a question to check if the hardware is present physically
                                    before failing if the test follows INFO/CONCLUSION format. Default set to False
                                    For example, Check SSD is fully inserted.
                    test_name: Name of the test to perform
                    test_command: Test's Command to perform
    :return:
    """
    hardware_check = kwargs['hardware_check'] if 'hardware_check' in kwargs else False
    test_name = kwargs['test_name']
    result = False
    must_validate = False
    hardware_check_cnt = 1 if hardware_check else 0

    while not result:
        result, must_validate, hardware_check_cnt = send_evaluate_cmd(
            hardware_check_cnt=hardware_check_cnt,
            conn=conn,
            expectphrase=expectphrase,
            timeout=timeout,
            retry=retry,
            **kwargs
        )

        # Prompt Message to operator to check the respective hardware
        if hardware_check:
            if hardware_check_cnt <= 0:
                break

            hw_result, hardware_check_cnt = util.check_hardware(hardware_check_cnt, test_name)

            if not hw_result:
                return False, False
        else:
            break

    return result, must_validate


def send_evaluate_cmd(hardware_check_cnt, conn, expectphrase, timeout=1800, retry=0, **kwargs):
    """Send Evaluate CMD

    Send test command and evaluate buffer response, if it was a PASS, FAIL or RESULT

    :param hardware_check_cnt:
    :param conn:
    :param expectphrase:
    :param timeout:
    :param retry:
    :param kwargs: Required:
                    - hardware_check: Flag to trigger a question to check if the hardware is present physically
                                    before failing if the test follows INFO/CONCLUSION format. Default set to False
                                    For example, Check SSD is fully inserted.
                    - test_name: Name of the test to perform
                    - test_command: Test's Command to perform
    :return:
    """
    test_command = kwargs['test_command']
    hardware_check_count = hardware_check_cnt
    must_validate = False
    conclusion_flag = False
    result = False

    start_time = time.time()
    log.info('Functional Test Name : {}'.format(test_command))
    util.sende(conn, text=test_command + '\r', expectphrase=expectphrase, timeout=timeout, retry=retry)
    util.sleep(10)
    buffer = capture_meas(conn.recbuf)
    for line in buffer.splitlines():
        if "INFO:" in line:
            log.info('::   {}'.format(line))
            if conclusion_flag:
                log.warning('INFO found after CONCLUSION.')
                result = False
                break
        if "CONCLUSION:" in line:
            log.info('::   {}'.format(line))
            conclusion_flag = True
            line = line.replace('CONCLUSION:', '').strip()
            if line not in ['PASSED', 'FAILED', 'RESULT']:
                log.warning('CONCLUSION not compliant with standard format.')
                result = False
                break
            if "PASSED" in line:
                result = True
                hardware_check_count -= 1
            elif "RESULT" in line:
                log.info('Validate Test as required.')
                must_validate = True
                result = True
                hardware_check_count -= 1

    end_time = time.time()
    log.info('Time Elapsed : {}'.format(end_time - start_time))

    return result, must_validate, hardware_check_count


def save_logs(conn, expectphrase, timeout=300, **kwargs):
    """Save Logs

    Parse the log name, compress and save the logs

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param test_name: Test name (to be used as folder name)
    :param retry: number of retries
    :param timeout: Wait time in seconds
    :param kwargs: Required:
                    - credentials: User credentials - {'id': username, 'password': password}
                        - id : This is the user of the server to do the scp files
                        - password: This is the password of the server to do the scp files
                    - destination_source_server: This is the ip images server
                    - destination_path: This is the destination path to be stored the files
                    - buffer: Functional test output buffer
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    test_name = kwargs['test_name']
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    destination_path = kwargs['destination_path']
    destination_server = kwargs['destination_server']
    buffer = kwargs['buffer'] if 'buffer' in kwargs else conn.recbuf

    log.debug('=============================================================')
    folder_name = ''
    serial_number = lib.get_serial_number()
    date = datetime.datetime.now().strftime('%m%d20%y%H%M%S')
    folder_name = serial_number + '_' + "".join(test_name.split()) + '_' + date
    log.info('Folder Name : {}'.format(folder_name))
    log_available = False

    for line in buffer.splitlines():
        if 'LOG IN' in line.upper():
            log_available = True
            log.debug('=============================================================')
            # Parse the source folder and filename
            source_list, file_list = get_logname(buffer=line)
            log.debug('=============================================================')
            # Create a folder to copy the log files
            util.mkdir(conn, folder_name, prompt=expectphrase)
            log.debug('=============================================================')
            # Copy the log files to newly created folder and compress the folder
            log.debug('Copying to {} & Compressing log files... '.format(folder_name))
            if compress_logs(conn,
                             source_list=source_list,
                             file_list=file_list,
                             folder_name=folder_name,
                             expectphrase=expectphrase,
                             timeout=timeout):
                log.debug('=============================================================')
                # Copy the compressed file to the /tftpboot of server hosting test
                log.debug('Copying compressed file {} to server ..'.format(folder_name))
                if util.scp(
                    conn=conn,
                    username=username,
                    password=password,
                    source_path='',
                    destination_path=destination_path,
                    destination_server=destination_server,
                    file='{}.tar.gz'.format(folder_name),
                    copy_type='2',
                    skip_check=True,
                    prompt=expectphrase,
                    timeout=timeout
                ):
                    log.debug('=============================================================')
                    log.info('Tar Log file {}.tar.gz copied to {}'.format(folder_name, destination_path))
                    log.debug('=============================================================')
                    # Save file name in cache
                    lib.cache_data('LOG File_{}'.format(lib.get_container_name()), '{}.tar.gz'.format(folder_name))
                    return True

    if not log_available:
        log.info('Logs not available!')
        return True
    log.warning('Unable to save log files.')
    userdict['operator_message'] = util.operator_message(
        error_message='Error: {} - Unable to save logs'.format(util.whoami()),
        resolution_message='Call Support',
    )
    return False


def get_logname(**kwargs):
    """Get logname

    Parse the source path and file name

    :param kwargs: Required:
                    - buffer: Buffer with log name
    :return: list of path and file name
    """
    buffer = kwargs['buffer']
    file_list = []
    source_list = []
    regex = re.compile('^(\/.*)+\/.*$')
    logs_list = [x for x in buffer.split(' ') if regex.match(x)]
    log.debug('List of Logs: {}'.format(logs_list))

    for file in logs_list:
        source_list.append(re.match('^(\/.*)+(\/.*)$', file).group(1))
        file_list.append(re.match('^(\/.*)+(\/.*)$', file).group(2).replace('/', ''))

    log.info('Source List: {}'.format(source_list))
    log.info('File List: {}'.format(file_list))
    return source_list, file_list


def compress_logs(conn, expectphrase, timeout=300, **kwargs):
    """Compress Logs

    Copy & Compress log files

    :param kwargs: Required:
                    - source_list: list of path
                    - file_list: list of log file names
                    - folder_name: Folder name to which log files are copied and compressed
    :return: True or False
    """
    result = False
    source_list = kwargs['source_list']
    file_list = kwargs['file_list']
    folder_name = kwargs['folder_name']

    if file_list:
        for source, log_file in zip(source_list, file_list):
            log.debug('Copy File: {}'.format(log_file))
            if not util.copy(conn, source, folder_name, log_file, expectphrase):
                log.debug('Unable to copy file {}'.format(log_file))
            result = True
        if result:
            result = util.tar(conn, folder_name, folder_name, expectphrase, timeout=timeout)
            log.info('Compressed File: {}.tar.gz'.format(folder_name))

    return result


def upload_logs(conn, expectphrase, timeout=300, **kwargs):
    """Upload Logs

    upload compressed logs to measurement link. Should use check_remote_ts() in case using a remote TS.

    :param conn: UUT's connection object
    :param expectphrase: Expected Phrase/Value
    :param timeout: Wait time in seconds
    :param kwargs: Required:
                    - test_name: Test Name (used to save in measurement)
                    - credentials: User credentials - {'id': username, 'password': password}
                        - id : This is the user of the server to do the scp files
                        - password: This is the password of the server to do the scp files
                    - source_path: This is the source path of the files
                    - destination_path: This is the destination path to be stored the files
    :return: True or False
    """
    userdict = lib.apdicts.userdict
    try:
        test_name = kwargs['test_name']
        username = kwargs['credentials']['id']
        password = kwargs['credentials']['password']
        source_path = kwargs['source_path']
        destination_path = kwargs['destination_path'] if 'destination_path' in kwargs else 'tftpboot'

        if lib.get_cached_data('LOG File_{}'.format(lib.get_container_name())) is not None:
            remote_server = lib.get_cached_data('remote_ts_{}'.format(lib.get_container_name()))
            server = lib.get_hostname()
            file = lib.get_cached_data('LOG File_{}'.format(lib.get_container_name()))
            log.info('Remote Server: {}'.format(remote_server))
            log.info('Server: {}'.format(server))
            log.info('File to be copied: {}'.format(file))
            util.send(conn, '\r')
            # If using remote TS, copy the file from tftp server to apollo machine
            if remote_server is not None:
                util.scp(
                    conn=conn,
                    username=username,
                    password=password,
                    source_server=remote_server,
                    source_path=source_path,
                    destination_server=server,
                    destination_path=destination_path,
                    copy_type='3',
                    file=file,
                    prompt=expectphrase,
                    timeout=timeout
                )
                # Remove file
                util.send(conn,
                          'ssh {}@{} "rm /{}/{}"\r'.format(username, remote_server, destination_path, file),
                          expectphrase=['(yes/no)', 'password', '(y/n)'],
                          regex=True,
                          timeout=timeout)
                if '(yes/no)' in conn.recbuf or '(y/n)' in conn.recbuf:
                    util.sende(conn, 'yes\r', expectphrase='password', timeout=timeout, regex=True)
                util.send(conn, '{}\r'.format(password), expectphrase=expectphrase, timeout=timeout, regex=True)

            # Upload log file to measurement link
            log.info('Uploading file in Measurement: {}'.format(file))
            util.upload_measurement(
                limit_name='{} files'.format(test_name),
                capture_value='/{}/{}'.format(destination_path, file),
                validation_type='file'
            )
            util.sleep(30)
            lib.delete_cached_data('LOG File_{}'.format(lib.get_container_name()))
    except Exception as e:
        log.warning('Unable to upload logs. Error: {}'.format(e))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to upload logs'.format(util.whoami()),
            resolution_message='Call Support',
        )
        return False

    return True


def run_memory_size_test(**rommon_info):
    """run memtest with memsize
    As TDE, te will run_memory_size_test will determine the memsize for memtest

    :param rommon_info: Dictionary with Rommon info
    :return Total memory size as integer
    """
    total_dim = 0

    cpu_memsize = int(filter(str.isdigit, rommon_info['rommon']['info']['Processor memory amount']))
    log.info('cpu_memsize: {}'.format(cpu_memsize))

    if 'DIMM0' in rommon_info['rommon']['info']:
        info_dimm0 = rommon_info['rommon']['info']['DIMM0']
        log.info('DIMM0: {}'.format(info_dimm0))
        total_dim += 1
        if 'DIMM1' in rommon_info['rommon']['info']:
            info_dimm1 = rommon_info['rommon']['DIMM1']
            log.info('DIMM1: {}'.format(info_dimm1))
            total_dim += 1

        log.info('Total Dim: {}'.format(total_dim))
        total_memsize = cpu_memsize / total_dim
        if total_dim == 2:
            total_memsize = cpu_memsize + 1024
        return total_memsize


def diag_mio_show_inventory(conn, keys=None, delimiter=': ', timeout=200, skip_fail_pars_list=False):
    """Show menush inventory.
    If fields is not specified, the script will attempt to capture every
    field in the output.

    See example in show().

    :param conn: UUT's connection object
    :param keys: List pf keys to display
    :param delimiter: Character delimiter to obtain key value pairs
    :return captured_fields as dictionary
    """
    if not keys:
        keys = []
    info = show(conn, util.whoami().replace('_', ' '), keys=keys, delimiter=delimiter,
                timeout=timeout, skip_fail_parse_list=skip_fail_pars_list)

    return info


def show(conn, command, keys=None, delimiter=':', timeout=200, skip_fail_parse_list=False):
    """Show contents of a command and capture the desired fields.

    If fields is not specified, the script will attempt to capture every
    field in the output.

    Example:
    ======
    show('info', keys=['ADDRESS', 'SERVER', 'GATEWAY'], delimiter='=')

    Sample output:
    ======
    rommon #1> show info


    Cisco Systems ROMMON Version (1.0(12)13) #0: Thu Aug 28 15:55:27 PDT 2008


    Platform Identification and Boot Information:
             Controller Type: 0x0520
               Platform Name: ASA5505

      Configuration Register: 0x00000001


    Interface Device Information:
      Ethernet0/0: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/1: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/2: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/3: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/4: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/5: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/6: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11
      Ethernet0/7: Y88ACS06, PCI: bus-0, slot-12, fct-0, rev-16, irq-11


    ROMMON Variable Settings:
      ADDRESS=0.0.0.0
      SERVER=0.0.0.0
      GATEWAY=0.0.0.0
      PORT=Ethernet0/0
      VLAN=untagged
      IMAGE=
      CONFIG=
      LINKTIMEOUT=200
      PKTTIMEOUT=4

      RETRY=20


    Sample captured_fields:
    dict = {'ADDRESS': '0.0.0.0', 'SERVER': '0.0.0.0', 'GATEWAY': '0.0.0.0'}

    :param conn: UUT's conection
    :param command: Command to send and display values
    :param keys: Keys list to get
    :param delimiter: Delimiter character to obtain key-value pairs
    :param timeout: Wait time in seconds
    :param skip_fail_parse_list: Ignore any error/fail message if True
    :return Dictionary with the found values
    """
    if not keys:
        keys = []
    if type(keys) in types.StringTypes:
        keys = [keys]

    util.sende(conn, '{}\r'.format(command), expectphrase=prompt, timeout=timeout, regex=True)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_parse_list):
        error_message = 'Error phrase found'
        log.warning(error_message)

    if 'usage:' in conn.recbuf:
        return None

    buffer = capture_meas(conn.recbuf)
    return util.parse_for_key_value_pair(buffer, keys=keys, delimiter=delimiter)


def check_firmware_version(expected_version, current_version, firmware):
    """ Check firmware version.

    Function to compare the version captured and the version expected for a certain
    firmware.

    :param firmware: firmware to be checked.
    :param expected_version: Version Captured from the UUT.
    :param current_version: Version Expected for the specific firmware.
    :return boolean
    """
    userdict = lib.apdicts.userdict
    result = False

    if userdict['menush']['info']:
        if expected_version != current_version:
            log.info('{} Version Needs to be update to {}! found {}'.
                     format(firmware, expected_version, current_version))
            result = True
        else:
            log.info('{} Version Up-to-date {}!'.format(firmware, current_version))

    return result


def fan_test(conn, expectphrase=prompt, retry=1, timeout=200, skip_fail_pars_list=False, **kwargs):
    """fan test

    Function to set and validate Fan Speed.

    As TDE, will provide method for fan test on uut.
    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
                    - tests: List of Fan level to be set and validated
                    - fanlevels: Dictionary containg Fan quantity and Fan levels supported by diag. For example,
                                'fanlevels': {
                                        'fan_number': 12,
                                        'FAN_SPEED_LEVEL_L0': '40',
                                        'FAN_SPEED_LEVEL_L1': '50',
                                        'FAN_SPEED_LEVEL_L2': '60',
                                        },
    :return:
    """
    tests = kwargs['tests']
    fanlevels = kwargs['fanlevels']

    userdict = lib.apdicts.userdict
    result = True
    result_msg = ''

    for fantest in tests:
        log.info('Testing Fan test: {}%'.format(fantest))
        fanlevel = fanlevels[fantest]
        log.info('Testing Fan Speed: {}%'.format(fanlevel))

        test_command = 'diag mio utils fan speed-{}\r'.format(fanlevel)
        log.info('***************************************')
        log.info('Fan setting at speed-{}'.format(fanlevel))
        log.info('***************************************')
        if not run_functional_test(
                conn=conn,
                test_name=lib.getstepdata()['stepdict']['name'],
                test_command=test_command,
                expectphrase=expectphrase,
                retry=retry,
                timeout=timeout,
                skip_fail_pars_list=skip_fail_pars_list
        ):
            result = False
            result_msg = 'Unable to set and test fan level {}'.format(fantest)
            break

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )

    return result


def read_temperatures(conn, expectphrase=prompt, retry=0, timeout=200, skip_fail_pars_list=False):
    """read temperatures

    Function to capture and evaluate temperatures on MIO.

    As TDE, will provide a method to read temperatures on uut
    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    """
    userdict = lib.apdicts.userdict
    conns = lib.getconnections()
    result = True
    result_msg = ''

    util.sende(conn, 'diag mio show temp\r', expectphrase=expectphrase, retry=retry, timeout=timeout)
    if userdict['diag_flag']:
        buffer = capture_meas(conn.recbuf)
        for x, line in enumerate(buffer.splitlines()):

            data = util.parse_for_key_value_pair(''.join(buffer), [], ': ')

            # Basin Temperature
            basinfronttemp = Decimal(data['BASIN Front Temp'].split()[0])
            basinreartemp = Decimal(data['BASIN Rear Temp'].split()[0])
            log.info('Basin Front Temperature = {}'.format(basinfronttemp))
            log.info('Basin Rear Temperature = {}'.format(basinreartemp))
            if basinfronttemp > 65 or basinreartemp > 65:
                log.warning('Basin Sensor is high. Should be less than 65C')
                result = False

            # Bridge Temperature
            bridgereartemp = Decimal(data['BRIDGE Rear Temp'].split()[0])
            bridgefronttemp = Decimal(data['BRIDGE Front Temp'].split()[0])
            log.info('Bridge Rear Temperature = {}'.format(bridgereartemp))
            log.info('Bridge Front Temperature = {}'.format(bridgefronttemp))
            if bridgereartemp > 75 or bridgefronttemp > 75:
                log.warning('Bridge Rear Sensor is high. Should be less than 75C')
                result = False

            # Netmod Temperature
            netmod2temp = Decimal(data['EPM2 Temp'].split()[0])
            netmod3temp = Decimal(data['EPM3 Temp'].split()[0])
            log.info('NetMod2 Temperature = {}'.format(netmod2temp))
            log.info('NetMod3 Temperature = {}'.format(netmod3temp))
            if netmod2temp > 65 or netmod3temp > 65:
                log.warning('NetMod temperature is high. Should be less than 65C')
                result = False

            # CPU Temperature
            for index in range(1, 9):
                if 'CPU Core {} Temp'.format(index - 1) in data:
                    bridgecputemp = Decimal(data['CPU Core {} Temp'.format(index - 1)].split()[0])
                    log.info('Intel Broadwell Core {} Temperature = {}'.format(index - 1, bridgecputemp))
                    if bridgecputemp > 55:
                        log.warning('Intel Broadwell Core {} Sensor is high. Should be less than 55C'.format(index - 1))
                        result = False
                        break

            # Bridge Trident Temperature
            for line_bridge_trident in data:
                if 'BRIDGE TRIDENT Temp' in line_bridge_trident:
                    bridgetemp = data[line_bridge_trident].split(',')
                    bridgetridnettemp = Decimal(bridgetemp[0].split('current=')[1])
                    log.info('{} = {}'.format(line_bridge_trident, bridgetridnettemp))
                    bridgetridnetpeak = Decimal(bridgetemp[1].split('peak=')[1])
                    if bridgetridnettemp > bridgetridnetpeak:
                        log.warning('{} is high. Should be less than 63C'.format(line_bridge_trident))
                        result = False
                        break

            if not result:
                # Turn off chassis
                conns['PWR1'].power_off()
                conns['PWR2'].power_off()
    else:
        for x, line in enumerate(conn.recbuf.splitlines()):
            # TODO cleanup function
            if 'CARD TYPE BASIN' in line:
                # Basin front temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:-1]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:-1]))
                basinfronttemp = Decimal(data['Front Temperature sensor'].split()[0])
                log.info('Basin Front Temperature = {}'.format(basinfronttemp))

                util.upload_measurement(
                    limit_name='Basin Front Sensor',
                    capture_value=float(basinfronttemp),
                    limit_value=float(65),
                    validation_type='max'
                )

                if basinfronttemp > 65:
                    log.warning('Basin Front Sensor is too high. Should be less than 65C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

                # Basin rear temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:-1]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:-1]))
                basinreartemp = Decimal(data['Rear Temperature sensor'].split()[0])
                log.info('Basin Rear Temperature = {}'.format(basinreartemp))

                util.upload_measurement(
                    limit_name='Basin Rear Sensor',
                    capture_value=float(basinreartemp),
                    limit_value=float(65),
                    validation_type='max')

                if basinreartemp > 65:
                    log.warning('Basin Rear Sensor is too high. Should be less than 65C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

            if 'CARD TYPE BRIDGE REAR' in line:
                # Bridge rear temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:(x + 3)]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:(x + 2)]))
                bridgereartemp = Decimal(data['Temperature'].split()[0])
                log.info('Bridge Rear Temperature = {}'.format(bridgereartemp))

                util.upload_measurement(
                    limit_name='Bridge Rear Sensor',
                    capture_value=float(bridgereartemp),
                    limit_value=float(75),
                    validation_type='max'
                )

                if bridgereartemp > 75:
                    log.warning('Bridge Rear Sensor is too high. Should be less than 75C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

            if 'CARD TYPE BRIDGE FRONT' in line:
                # Bridge front temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:(x + 3)]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:(x + 2)]))
                bridgefronttemp = Decimal(data['Temperature'].split()[0])
                log.info('Bridge Front Temperature = {}'.format(bridgefronttemp))

                util.upload_measurement(
                    limit_name='Bridge Front Sensor',
                    capture_value=float(bridgefronttemp),
                    limit_value=float(75),
                    validation_type='max'
                )

                if bridgefronttemp > 75:
                    log.warning('Bridge Front Sensor is too high. Should be less than 75C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

            if 'CARD TYPE EPM2' in line:
                # Bridge front temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:(x + 3)]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:(x + 2)]))
                netmod2temp = Decimal(data['Temperature'].split()[0])
                log.info('NetMod2 Temperature = {}'.format(netmod2temp))

                util.upload_measurement(
                    limit_name='NetMod2 Temperature',
                    capture_value=float(netmod2temp),
                    limit_value=float(65),
                    validation_type='max'
                )

                if netmod2temp > 65:
                    log.warning('NetMod2 temperature is too high. Should be less than 65C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

            if 'CARD TYPE EPM3' in line:
                # Bridge front temperature
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)[x:(x + 3)]), [], '= ')
                # log.info('x:{}, {}'.format(x, conn.recbuf.splitlines(True)[x:(x + 2)]))
                netmod3temp = Decimal(data['Temperature'].split()[0])
                log.info('NetMod3 Temperature = {}'.format(netmod3temp))

                util.upload_measurement(
                    limit_name='NetMod3 Temperature',
                    capture_value=float(netmod3temp),
                    limit_value=float(65),
                    validation_type='max'
                )

                if netmod3temp > 65:
                    log.warning('NetMod3 temperature is too high. Should be less than 65C')
                    # turn off chassis bc MIO is too hot...
                    conns['PWR1'].power_off()
                    conns['PWR2'].power_off()
                    result = False
                    break

            if 'Intel Broadwell' in line:
                # Bridge CPU temperatures
                # log.info('Intel Broadwell')
                data = util.parse_for_key_value_pair(''.join(conn.recbuf.splitlines(True)), [], '= ')
                for index in range(1, 9):
                    bridgecputemp = Decimal(data['Core {} Temperature'.format(index - 1)].split()[0])
                    log.info('Intel Broadwell Core {} Temperature = {}'.format(index - 1, bridgecputemp))

                    util.upload_measurement(
                        limit_name='Intel Broadwell Core {}'.format(index - 1),
                        capture_value=float(bridgecputemp),
                        limit_value=float(55),
                        validation_type='max'
                    )

                    if bridgecputemp > 55:
                        log.warning('Intel Broadwell Core {} Sensor is high. Should be less than 55C'.format(index - 1))
                        # turn off chassis bc MIO is too hot...
                        conns['PWR1'].power_off()
                        conns['PWR2'].power_off()
                        result = False
                        break
                if not result:
                    break

            if 'CARD TYPE BRIDGE TRIDENT' in line:
                # Bridge Trident temperatures
                data = conn.recbuf.splitlines(True)[x:-1]
                result = False
                for index, line_bridge_trident in enumerate(data):
                    if 'current=' in line_bridge_trident:
                        result = True
                        # log.info('line_bridge_trident {}'.format(line_bridge_trident))
                        bridgetridnettemp = Decimal((line_bridge_trident.split(',')[0]).split('current=')[1])
                        log.info('Bridge Trident {} Temperature = {}'.format(index - 1, bridgetridnettemp))
                        bridgetridnetpeak = Decimal((line_bridge_trident.split(',')[1]).split('peak=')[1])
                        util.upload_measurement(
                            limit_name='Bridge Trident Monitor {}'.format(index - 1),
                            capture_value=float(bridgetridnettemp),
                            limit_value=float(bridgetridnetpeak),
                            validation_type='max'
                        )

                        if bridgetridnettemp > bridgetridnetpeak:
                            log.warning('Bridge Trident Monitor {} is high. Should be less than 63C'.format(index - 1))
                            # turn off chassis bc MIO is too hot...
                            conns['PWR1'].power_off()
                            conns['PWR2'].power_off()
                            result = False
                            break
                if not result:
                    break

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )

    return result


def capture_dimm_location(**kwargs):
    """capture dimm location

    As TDE, will provide method to parse dimm location from uut.
    :param kwargs
        - memory: Dictionary of memory details of Location, Vendor and Type
    """
    memory = kwargs['memory'] if 'memory' in kwargs else None

    result_msg = ''
    # DRAM ChannelA-DIMM 0 BANK 0 should be populated
    # DRAM ChannelB-DIMM 0 BANK 2 should be populated
    if 'ChannelA-DIMM 0' in memory['Location'] or 'ChannelB-DIMM 0' in memory['Location']:
        if 'Empty' in memory['Vendor'] or 'Unknown' in memory['Type']:
            result_msg = 'Wrong Memory Location: {}, DRAM Should be populated '.format(memory['Location'])
            log.warning(result_msg)
            return result_msg, False
    # DRAM ChannelA-DIMM 1 BANK 1 should not be populated
    # DRAM ChannelB-DIMM 1 BANK 3 should not be populated
    elif 'ChannelA-DIMM 1' in memory['Location'] or 'ChannelB-DIMM 1' in memory['Location']:
        if 'Empty' not in memory['Vendor'] or 'Unknown' not in memory['Type']:
            result_msg = 'Wrong Memory Location: {}, DRAM Should not be populated '.format(memory['Location'])
            log.warning(result_msg)
            return result_msg, False
    # Should not getting here
    else:
        result_msg = 'Memory Location {}, not determined '.format(memory['Location'])
        log.warning(result_msg)
        return result_msg, False

    return result_msg, True


def capture_dimm_size(**kwargs):
    """capture dimm size

    As TDE, will provide method to parse dimm size from uut.
    :param kwargs
        - memory: Dictionary of memory details of Location, Vendor and Type
        - pid :  UUT PID
    """
    memory = kwargs['memory'] if 'memory' in kwargs else None
    pid = kwargs['pid']

    result_msg = ''
    userdict = lib.apdicts.userdict

    # TODO: Remove usage of userdict
    # DRAM ChannelA-DIMM 0 BANK 0 should be populated
    # DRAM ChannelB-DIMM 0 BANK 2 should be populated
    if 'ChannelA-DIMM 0' in memory['Location'] or 'ChannelB-DIMM 0' in memory['Location']:
        return result_msg, util.verify_value(
            expected=userdict[pid]['dimm_size'],
            captured=memory['Size'],
            operator_type=operator.eq)
    # DRAM ChannelA-DIMM 1 BANK 1 should not be populated
    # DRAM ChannelB-DIMM 1 BANK 3 should not be populated
    elif 'ChannelA-DIMM 1' in memory['Location'] or 'ChannelB-DIMM 1' in memory['Location']:
        if '0 GB' not in memory['Size']:
            result_msg = 'Wrong Memory Size, DRAM Size should be 0 GB'
            log.warning(result_msg)
            return result_msg, False
    # Should not getting here
    else:
        result_msg = 'Memory Size {}, not determined '.format(memory['Size'])
        log.warning(result_msg)
        return result_msg, False
    return result_msg, True


def capture_dimm_part_number(**kwargs):
    """capture dimm size

    As TDE, will provide method to parse dimm part number from uut.
    :param kwargs
        - memory: Dictionary of memory details of Location, Vendor and Type
        - pid :  UUT PID
    """
    memory = kwargs['memory'] if 'memory' in kwargs else None
    pid = kwargs['pid']

    result_msg = ''

    userdict = lib.apdicts.userdict
    # TODO: Remove usage of userdict
    # DRAM ChannelA-DIMM 0 BANK 0 should be populated
    # DRAM ChannelB-DIMM 0 BANK 2 should be populated
    if 'ChannelA-DIMM 0' in memory['Location'] or 'ChannelB-DIMM 0' in memory['Location']:
        regex = re.compile(memory['Part Number'] + '*')
        if not [m.group() for l in userdict[pid]['dimm_part_number'] for m
                in [regex.search(l)] if m]:
            result_msg = 'Wrong Part Number: {}, not found in valid Part ' \
                         'Numbers list: {}'.format(memory['Part Number'],
                                                   userdict[pid]['dimm_part_number'])
            log.warning(result_msg)
            return result_msg, False
    # DRAM ChannelA-DIMM 1 BANK 1 should not be populated
    # DRAM ChannelB-DIMM 1 BANK 3 should not be populated
    elif 'ChannelA-DIMM 1' in memory['Location'] or 'ChannelB-DIMM 1' in memory['Location']:
        if 'Empty' not in memory['Part Number']:
            result_msg = 'Part Number {} should be Empty'.format(memory['Part Number'])
            log.warning(result_msg)
            return result_msg, False
    # Should not getting here
    else:
        result_msg = 'Memory Part Number {}, not determined '.format(memory['Part Number'])
        log.warning(result_msg)
        return result_msg, False

    return result_msg, True


def get_drams_info(buffer):
    """Get DRAMS Info

    Campture DRAMs information from Connection Buffer

    :param buffer:
    :return:
    """
    drams = []
    buffer = "".join([s for s in buffer.splitlines(True) if s.strip("\r\n")])
    for x, line in enumerate(buffer.splitlines()):
        dram = {}
        if 'DRAM-A' in line or 'DRAM-B' in line:
            data = buffer.splitlines()[x:][:8]
            for index, element in enumerate(data):
                templine = re.sub(r'|'.join(map(re.escape, ['DRAM-A', 'DRAM-B'])), '', element)
                if ':' in templine:
                    keyname = templine.split(':')[0].strip()
                    keyvalue = templine.split(':')[1].strip()
                    dram[keyname] = keyvalue
            drams.append(dram)

    return drams


def capture_system_info(conn,
                        expectphrase=prompt,
                        retry=1,
                        timeout=200,
                        skip_fail_pars_list=False,
                        skip_fail=False,
                        **kwargs):
    """capture system info

    As TDE, will provide method to test capture system info from uut.
    :param conn: UUT's connection
    :param expectphrase: Expected Phrase/Value
    :param retry: Number of retries
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Ignore any error/fail message if True
    :param skip_fail: Flag to ignore test failure . Default is False
    :param kwargs :
        - pid: UUT PID
    :return:
    """
    pid = kwargs['pid']
    userdict = lib.apdicts.userdict
    result = True
    result_msg = ''
    results = []

    util.sende(conn, 'diag mio show inventory\r', expectphrase=expectphrase,
               retry=retry, timeout=timeout)

    buffer = capture_meas(conn.recbuf)
    data = util.parse_for_key_value_pair(buffer, keys=[], delimiter=':')
    userdict['capture_system_info'] = data

    log.info('Validating Processor Family')
    # TODO: Remove usage of userdict
    results.append(
        util.verify_value(
            expected=userdict[pid]['processor_family'],
            captured=data['Family'],
            operator_type=operator.eq,
            skip_fail=skip_fail
        ))
    limit_name = 'Processor Family'
    limit_value = data['Family']
    util.upload_measurement(limit_name, limit_value)

    log.info('Validating Processor Version')
    results.append(
        util.verify_value(
            expected=userdict[pid]['processor_version'],
            captured=data['Version'],
            operator_type=operator.eq,
            skip_fail=skip_fail
        ))

    limit_name = 'Processor Version'
    limit_value = data['Version']
    util.upload_measurement(limit_name, limit_value)

    # Create list of dictionaries for each dram found
    """
    DRAM-A   Vendor : Unknown
       Location : ChannelA-DIMM 0 BANK 0
           Type : DDR3 (Unregistered)
           Size : 8 GB
          Speed : 1600 MHz
    Part Number : SH5721G823AUNUMSD2
             SN : 30315232

    [{'Vendor': '',
    'Location': '',
    'Type': '',
    'Size': '',
    'Speed': '',
    'Part Number': '',
    'SN': ''},]
    """
    drams = get_drams_info(buffer)

    # Validate each DRAM value
    log.info('Validating DRAMs')
    for x, dimm in enumerate(drams):
        log.info('*' * 30)

        log.info('Validating DRAM - Location')
        log.info('Memory Location: {}'.format(dimm['Location']))
        result_msg, result = capture_dimm_location(memory=dimm)
        results.append(result)

        log.info('Validating DRAM - Size')
        log.info('Memory Size: {},'.format(dimm['Size']))
        result_msg, result = capture_dimm_size(memory=dimm, pid=pid)
        results.append(result)

        log.info('Validating DRAM - Part Number')
        log.info('dimm value {}'.format(dimm))
        log.info('Memory Part Number: {},'.format(dimm['Part Number']))
        result_msg, result = capture_dimm_part_number(memory=dimm, pid=pid)
        results.append(result)

        log.info('Logging DRAM - Serial Number')
        log.info('Memory Serial Number: {},'.format(dimm['SN']))

        log.info('Logging DRAM - Speed')
        log.info('Memory Speed: {},'.format(dimm['Speed']))

        log.info('Logging DRAM - Type')
        log.info('Memory Type: {},'.format(dimm['Type']))

        log.info('Logging DRAM - Vendor')
        log.info('Memory Vendor: {},'.format(dimm['Vendor']))

        # Capture Memmory info in Polaris measurement list.
        util.upload_measurement(limit_name='DRAM Location {}'.format(x),
                                capture_value=dimm['Location'])

        util.upload_measurement(limit_name='DRAM Size {}'.format(x),
                                capture_value=dimm['Size'] if not dimm['Size'] == '0 GB' else 'Not installed')

        # upload following measurements just in case memory is installed.
        if not 'Empty' == dimm['Vendor']:

            util.upload_measurement(limit_name='DRAM Part Number {}'.format(x),
                                    capture_value=dimm['Part Number'])

            util.upload_measurement(limit_name='DRAM Serial Number {}'.format(x),
                                    capture_value=dimm['SN'])

            util.upload_measurement(limit_name='DRAM Speed {}'.format(x),
                                    capture_value=dimm['Speed'])

            util.upload_measurement(limit_name='DRAM Type {}'.format(x),
                                    capture_value=dimm['Type'])

            util.upload_measurement(limit_name='DRAM Vendor {}'.format(x),
                                    capture_value=dimm['Vendor'])

    log.info('result list {}'.format(results))
    if len(results) != 14 or False in results:
        result = False

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(
            conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )

    return result


def obfl_erase(conn, expectphrase=prompt, retry=1, timeout=200, skip_fail_pars_list=False):
    """OBFL Erase
    As TDE, will provide a method to erase the OBFL on uut.

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True

    util.sende(conn, 'diag mio utils obfl-erase\r', expectphrase=expectphrase, retry=retry, timeout=timeout)

    if '0 blocks failed' not in conn.recbuf:
        result = False

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    limit_name = util.whoami().replace('_', ' ').title()
    result_msg = '{}: {}'.format(limit_name, result)
    log.info(result_msg)

    util.upload_measurement(limit_name, result)

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result),
            resolution_message='Call Support',
        )

    return result


def program_rtc(conn, expectphrase=prompt, timeout=100, skip_fail_pars_list=False, **kwargs):
    """Program RTC
    This routine will program the RTC clock time in the UUT

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:
        - rtc: current time (Format: YYYY.MM.DD-hh:mm:ss) For example, 2018.08.25-21:59:03
    :return:
    """
    rtc = kwargs['rtc']
    userdict = lib.apdicts.userdict
    result = True

    util.sende(conn, 'date -s {}\r'.format(rtc), expectphrase=expectphrase, timeout=200, regex=True)
    util.sende(conn, 'hwclock -w\r', expectphrase=expectphrase, timeout=200, regex=True)

    # Capture rtc date to measurement list on Polaris DB
    util.upload_measurement(limit_name='Program RTC',
                            capture_value=rtc)

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Other Errors'.format(util.whoami()),
            resolution_message='Call Support',
        )

    return result


def verify_rtc(conn, expectphrase=prompt, time_delta=45, timeout=200, skip_fail=False, skip_fail_pars_list=False):
    """Will capture  system time on UUT and Server and compare within limit.

    Sample output:
    ======
    > date
    Mon Apr 24 21:24:46 UTC 2017
    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param skip_fail: Flag to skip test failure. Default- False
    :param time_delta: Maximum time delta between current time and hardware clock
    """
    userdict = lib.apdicts.userdict
    result = True

    server_time = datetime.datetime.utcnow()
    log.info('Server UTC timestamp - Year: {}, Month: {}, Day: {}, Hour: {}, Minute: {}, Second: {}'.
             format(server_time.year, server_time.month, server_time.day,
                    server_time.hour, server_time.minute, server_time.second))

    util.sende(conn, 'date\r', expectphrase=expectphrase, timeout=timeout, regex=True)

    temp = conn.recbuf.splitlines()[1]

    uut_date = '{}:{}:{} {}:{}:{}'.format(
        temp.split()[5],
        str(time.strptime(temp.split()[1], '%b').tm_mon),
        temp.split()[2],
        temp.split()[3].split(':')[0],
        temp.split()[3].split(':')[1],
        temp.split()[3].split(':')[2]
    )

    uut_time = datetime.datetime.strptime(uut_date, '%Y:%m:%d %H:%M:%S')

    log.info('UUT UTC timestamp - Year: {}, Month: {}, Day: {}, Hour: {}, Minute: {}, Second: {}'.
             format(uut_time.year, uut_time.month, uut_time.day, uut_time.hour, uut_time.minute, uut_time.second))

    # Epoch validation
    unix_server_time = datetime.datetime.now().strftime('%s')

    util.send(conn, 'date +%s\r', expectphrase=expectphrase, timeout=200, regex=True)

    unix_uut_time = '{}'.format(conn.recbuf.splitlines()[1])

    date_unix_uut_time = datetime.datetime.fromtimestamp(int(unix_uut_time))
    date_unix_server_time = datetime.datetime.fromtimestamp(int(unix_server_time))

    time_difference = abs(date_unix_uut_time - date_unix_server_time)
    time_difference = int(time_difference.total_seconds())

    log.info('----------------------------------')
    log.info('server time: {}'.format(unix_server_time))
    log.info('uut time: {}'.format(unix_uut_time))
    log.info('allowable time delta: {}'.format(time_delta))
    log.info('time difference seconds: {}'.format(time_difference))
    log.info('----------------------------------')

    result = util.verify_value(
        expected=str(time_delta),
        captured=str(time_difference),
        operator_type=operator.ge,
        skip_fail=skip_fail,
    )

    util.upload_measurement(limit_name='Server EPOC time', capture_value=unix_server_time)
    util.upload_measurement(limit_name='UUT EPOC time', capture_value=unix_uut_time)
    util.upload_measurement(
        limit_name='EPOC delta',
        capture_value=time_difference,
        limit_value=time_delta,
        validation_type='max'
    )

    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed {}'.format(util.whoami()),
            resolution_message='Call technician',
        )

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # Specify Operator message
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed {}'.format(util.whoami()),
            resolution_message='',
        )
    return result


# TODO: IN QP , can this function be substited by run_functional_test ? (OR)
# we use 'diag mio utils idprom checksum dev-d ickenham'(confirmed by Hiep , fan == ickenham)

def mio_activate_fans(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Activate_fans
    As TDE, will define mio_activate_fans so that FST area can recognize Fans.

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:
        - fan_qty: In cases like Queens Park is not necessary to include in the command
            the fan number so we dont include this command when call function to sent without
            a fan number the command.
    :return:
    """
    fan_qty = kwargs['fan_qty'] if 'fan_qty' in kwargs else 1

    userdict = lib.apdicts.userdict
    fails_msg = ''

    for fan_no in range(fan_qty):
        result = True
        test_name = 'Activate Fan {}'.format(fan_no + 1)
        test_command = 'diag mio utils idprom checksum dev-d fan{}'.format(fan_no + 1)
        if fan_qty == 1:
            test_command = 'diag mio utils idprom checksum dev-d fan'

        if not run_functional_test(
                conn=conn,
                test_name=test_name,
                test_command=test_command,
                timeout=timeout,
                skip_fail_pars_list=skip_fail_pars_list,
        ):
            log.error('Fan {} Activation Failed, removing fan_mutex file from tmp'.format(fan_no + 1))

            util.sende(conn, 'rm /tmp/fan_mutex\r', expectphrase, timeout=200)
            if not run_functional_test(
                    conn=conn,
                    test_name=test_name,
                    test_command=test_command,
                    timeout=timeout,
                    skip_fail_pars_list=skip_fail_pars_list,
            ):
                result = False
                fails_msg += 'Fan {}. '.format(fan_no + 1)
        log.debug('Fan {} Activation Result: {}'.format(fan_no + 1, result))

    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed {}. {}'.format(util.whoami(), fails_msg),
            resolution_message='Call technician',
        )

    return result


def get_time(date_format='%m-%d-%y', seperator='-', hex=False):
    """Get time.

    Sample output:
    ======
    diagmon[0] 1 > cmostime 06/14/16 10:52:37
    Current date & time: 06/14/16  10:52:37
    diagmon[0] 2 >


    :param date_format: Date format
    :param seperator: Seperator for date format
    :param hex: Set true if value to be returned is hex
    :return:
    """
    now = datetime.datetime.now()
    date_program_format = '%m/%d/20%y %H:%M:%S'
    mfgdate = ''

    currentdate = now.strftime(date_program_format)
    mfgdate = now.strftime(date_format)

    if hex:
        nowmfg = mfgdate.split(seperator)
        mfgdate = ''
        log.info('Calculating hex value for current datetime..')
        for value in nowmfg:
            mfgdate += "{:02x}".format(int(value))
            log.info('MFG DATE: {}'.format(mfgdate))

    log.info('Current DateTime: {}'.format(currentdate))

    return mfgdate


def inventory_vs_scanned(conn, **kwargs):
    """Check Scanned vs Read from Sprom Value
    Function to check if value scanned and value from sprom are equal.
    example:
        Fields to check serial number in MIO:
            find_in_inventory='BACK PLANE  SN',
            scanned_value=userdict['sn']

    :param conn: UUT's connection object
    :param kwargs:
        - find_in_inventory: UUT inventory info to be checked
        - scanned_value: UUT recorded info
    :return:
    """
    find_in_inventory = kwargs['find_in_inventory']
    scanned_value = kwargs['scanned_value']

    userdict = lib.apdicts.userdict
    result = False
    programmed_value = diag_mio_show_inventory(conn, find_in_inventory)

    try:
        if programmed_value[find_in_inventory] == scanned_value:
            log.info('Scanned Value: {} = Programmed Value: {}'.format(
                scanned_value,
                programmed_value[find_in_inventory]
            ))
            result = True
        else:
            log.info('Scanned Value: {} is different than Programmed Value: {}'.format(
                scanned_value,
                programmed_value[find_in_inventory])
            )
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - {}'.format(
                    util.whoami(),
                    'Scanned Value: {} is different than Programmed Value: {}'.format(
                        scanned_value,
                        programmed_value[find_in_inventory])
                ),
                resolution_message='Call Support',
            )
    except Exception, e:
        log.error('Error: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), str(e)),
            resolution_message='Call Support',
        )

    return result


def verify_blade_sn(conn, **kwargs):
    """Verify Blade Serial Number.

    Function to verify blade Serial Number scanned vs Serial Number in Sprom.
    :param conn: UUT's connection object
    :param kwargs
        - blade_no: Blade slot number
        - scanned_sn: Recorded SN of corresponding blade
    :return:
    """
    blade_no = kwargs['blade_no']
    scanned_sn = kwargs['scanned_sn']

    userdict = lib.apdicts.userdict
    result = False
    cmd = 'diag blade{} show bldidprom'.format(blade_no)
    find_in_idprom = 'SERIAL NUM'
    programmed_sn = show(conn, cmd, find_in_idprom)

    try:
        if programmed_sn[find_in_idprom] == scanned_sn:
            log.info('Scanned Value: {} = Programmed Value: {}'.format(
                scanned_sn,
                programmed_sn[find_in_idprom]
            ))
            result = True
        else:
            log.info('Scanned Value: {} is different than Programmed Value: {}'.format(
                scanned_sn,
                programmed_sn[find_in_idprom])
            )
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - {}'.format(
                    util.whoami(),
                    'Scanned Value: {} is different than Programmed Value: {}'.format(
                        scanned_sn,
                        programmed_sn[find_in_idprom])
                ),
                resolution_message='Call Support',
            )
    except Exception, e:
        log.error('Error: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), str(e)),
            resolution_message='Call Support',
        )

    return result


def get_blade_images(conn, expectphrase=prompt, skip_fail_pars_list=False, timeout=300, **kwargs):
    """ Get Blade Images

        As TDE, will install blade images in order to test Blades
        :param conn: UUT's connection Object
        :param expectphrase: Phrase expected in response
        :param timeout: Wait time in seconds
        :param skip_fail_pars_list: Flag to catch error phrase. Default- False
        :param kwargs: Required:
                - credentials: User credentials - {'id': username, 'password': password}
                    - id : This is the user of the server to do the scp files
                    - password: This is the password of the server to do the scp files
                - source_server: This is the ip images server
                - destination_path: This is the destination path to be stored the files
                - img: This are the list of the legacy files fpga update
    """
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']
    destination_path = kwargs['destination_path']
    img = kwargs['img']

    userdict = lib.apdicts.userdict
    result = False
    source_path = 'tftpboot'
    if util.scp(
        conn=conn,
        username=username,
        password=password,
        source_server=source_server,
        source_path=source_path,
        destination_path=destination_path,
        file=img,
        prompt=expectphrase,
        timeout=timeout
    ):
        util.send(conn, 'cd /tmp\r', expectphrase, timeout)
        util.send(conn, 'getbladeimages /tmp/{}\r'.format(userdict['blade_image']), expectphrase, timeout)

        # TODO; raylai; new 2.1.8.0 does not have any prompt for getbladeimage is ready
        # if 'Blade images ready' in conn.recbuf:
        #     log.info('Extracting blade images...')
        #     util.send(conn, 'cd /tftpboot/{}\r'.format('blade-images'), expectphrase, timeout)
        #     if 'No such file or directory' in conn.recbuf:
        #         log.error('Error extracting Blade Images')
        #         userdict['operator_message'] = util.operator_message(
        #             error_message='Error: {} - Error extracting Blade Images'.format(util.whoami()),
        #             resolution_message='Call Support',
        #         )
        #     else:
        #         log.info('blade-images folder created successfully')
        result = True

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    return result


def install_patches(expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Install Patches

        As TDE, have to install necessary patches for Tests
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
            - server: Server IP address
            - patches: List of patches
            - patches_folder: Path of the patches in server
    :return:
    """
    patches_path = kwargs['patches_path']
    patches = kwargs['patches']
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']
    source_server = kwargs['source_server']

    lib.set_container_text('Install Patches...')
    userdict = lib.apdicts.userdict
    result = True
    conn = userdict['conn']

    try:
        log.info('---Installing Patches---')

        for path in patches:
            util.sende(conn, 'cd {}\r'.format(path), expectphrase, timeout=timeout)

            for patch in patches[path]:
                log.info('Installing patch {}'.format(patch))
                if not util.scp(
                        conn=conn,
                        username=username,
                        password=password,
                        source_server=source_server,
                        source_path=patches_path,
                        destination_path='',
                        file=patch,
                        prompt=expectphrase
                ):
                    result = False
                util.sende(conn, 'ls -l {}\r'.format(patch), expectphrase, timeout=timeout, regex=True)

                if 'No such file or directory' in conn.recbuf:
                    log.error('Cannot get Patch "{}"'.format(patch))
                    userdict['operator_message'] = util.operator_message(
                        error_message='Error: {} - Cannot get Patch "{}"'.format(util.whoami(), patch),
                        resolution_message='Call Support',
                    )
                    result = False

    except Exception as e:
        log.error('Error: Uanble to Enter MIO MenuSH: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), str(e)),
            resolution_message='Call Support',
        )
        result = False

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    return result


def power_redundancy(conn, expectphrase=prompt, pwr=[], retry=0, timeout=200):
    """power redundancy

    As TDE, will provide a method to test all Power Supplies on a Chassis.
    This function will keep just one Power Supply connection at a time, and check for communication with UUT

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail: Flag to skip test failure. Default- False
    :param pwr: A list containing the names of the connections of all Power Supplies on the Chassis
    :return:
    """
    log.info('--------------------------------')
    log.info('Power Redundancy/Fail-Over check')
    log.info('--------------------------------')

    userdict = lib.apdicts.userdict
    conns = lib.getconnections()
    result = True
    for ps_on in pwr:
        log.info('Power On {}'.format(ps_on))
        conns[ps_on].power_on()
        util.sleep(10)
        for ps_off in pwr:
            if ps_on != ps_off:
                log.info('Power Off {}'.format(ps_off))
                conns[ps_off].power_off()
                util.sleep(10)
        util.sleep(5)
        log.info('{} validation'.format(ps_on))
        try:
            util.sende(conn, '\r', expectphrase=expectphrase, retry=retry, timeout=timeout)
        except Exception:
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - Unable to power on unit - {}'.format(util.whoami(), ps_on),
                resolution_message='Call Support',
            )
            result = False
            break
        else:
            log.info('Communication Ok')

    log.info('-----Power On All Power Supplies-----')
    for ps_on in pwr:
        conns[ps_on].power_on()
        log.info('{} is On'.format(ps_on))

    return result


# TODO: check_rtc_time() and read_rtc_time() Are used just in KP. Are different from program_rtc() & verify_rtc()?
# Can the functions be merged? If not, add the function specific parameter to kwargs.
def check_rtc_time(conn,
                   test_command,
                   uut_time_pattern,
                   max_time_delta=200,
                   expectphrase=prompt,
                   timeout=200,
                   skip_fail_pars_list=False):
    """
    Check RTC time.

    Define function to check RTC time and compare against current time UTC within
    max time delta.
        :param conn: UUT's connection Object
        :param expectphrase: Phrase expected in response
        :param timeout: Wait time in seconds
        :param skip_fail_pars_list: Flag to catch error phrase. Default- False
        :uut_time_pattern: time format
        :max_time_delta: Maximum time difference allowed
    """
    userdict = lib.apdicts.userdict
    uut_time_str = ''
    log.info('Functional Test Name : {}'.format(test_command))

    system_time = datetime.datetime.utcnow()
    result = run_functional_test(
        conn=conn,
        test_name=test_command,
        test_command=test_command,
        skip_fail_pars_list=skip_fail_pars_list
    )

    for line in conn.recbuf.splitlines():
        # parse out uut time
        if 'UTC' in line:
            uut_time_str = line.strip()
            break

    # if fail to get uut time
    if not uut_time_str:
        result = False

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # compare system time to RTC time
    if result:
        time_delta = abs(datetime.datetime.strptime(uut_time_str, uut_time_pattern) -
                         system_time).total_seconds()
        log.debug('Time delta: {}'.format(time_delta))
        if time_delta > max_time_delta:
            result = False

    # Specify Operator messgae
    if not result:
        result_msg = 'RTC time check failed'
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )

    util.sleep(10)
    return result


def read_rtc_time(conn, test_command, uut_time_pattern, expectphrase=prompt, timeout=200, skip_fail_pars_list=False):
    """
    Read RTC time.

    Define function to read RTC time.
        :param conn: UUT's connection Object
        :param expectphrase: Phrase expected in response
        :param timeout: Wait time in seconds
        :param skip_fail_pars_list: Flag to catch error phrase. Default- False
        :uut_time_pattern: time format
        :max_time_delta: Maximum time difference allowed
    """
    userdict = lib.apdicts.userdict
    uut_time_str = ''
    uut_time = None
    log.info('Functional Test Name : {}'.format(test_command))

    result = run_functional_test(
        conn=conn,
        test_name=test_command,
        test_command=test_command,
        skip_fail_pars_list=skip_fail_pars_list
    )

    for line in conn.recbuf.splitlines():
        # parse out uut time
        if 'UTC' in line:
            uut_time_str = line.strip()
            break

    # if fail to get uut time
    if not uut_time_str:
        result = False

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    # compare system time to RTC time
    if result:
        uut_time = datetime.datetime.strptime(uut_time_str, uut_time_pattern)
        log.debug('RTC time: {}'.format(uut_time))

    # Specify Operator messgae
    if not result:
        result_msg = 'RTC time read failed'
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )

    return [result, uut_time]


def show_mio_idprom_field(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Show MIO IDPROM Field

    Returns given field (sn or pid) from MIO idprom, given a board (basin, bridge, fru)

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
            - board: Boards supported by diags (basin, bridge, fru)
            - field: Field supported by diags (sn or pid)
    :return:
    """
    board = kwargs['board']
    field = kwargs['field']

    field_value = ''
    cmd = 'diag mio show idprom {} -f {}\r'.format(board, field)
    util.sende(conn=conn, text=cmd, expectphrase=expectphrase)
    resp_dic = util.parse_for_key_value_pair(conn.recbuf, delimiter='=')
    for k, v in resp_dic.iteritems():
        field_value = v
        break

    return field_value


def read_mio_idprom_field(conn, expectphrase=prompt, timeout=200, skip_fail_pars_list=False, **kwargs):
    """Read MIO IDPROM Field

    Returns given mio board field according its offset and length

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs: Required:
            - board: Boards supported by diags (basin, bridge, fru)
            - offset: Field offset
            - length: Field length
    :return: Field value (String)
    """
    board = kwargs['board']
    offset = kwargs['offset']
    length = kwargs['length']

    field_value = ''
    cmd = 'diag mio utils idprom read -d {} -t ascii -o {} -r{}\r'.format(board, offset, length)
    util.sende(conn=conn, text=cmd, expectphrase=expectphrase)
    try:
        field_value = re.findall('^(.*)\nCONCLUSION', conn.recbuf, re.MULTILINE)[0].strip()
    except Exception, e:
        log.error('Error getting value. {}'.format(str(e)))

    return field_value


def check_remote_ts(conn, expectphrase=prompt):
    '''Check for Remote Terminal Server

    Function to determine if UUT is connected via a remote TS with WAN as
    opposed to LAN. The check is determined if the hostname of Apollo execution match
    UUT network connection hostname. userdict flag will be set for later consumption

    :param conn - UUT's Connection Object
    :param expectphrase: Expected Phrase/Value
    :return boolean
    '''
    userdict = lib.apdicts.userdict

    # Grab hostname of 10.1.1.1 server
    cmd = 'ssh {}@10.1.1.1 hostname \r'.format(userdict['apollo']['id'])
    util.sende(conn, cmd, expectphrase=['(yes/no)', '(y/n)', 'password'], timeout=60)
    if re.search('\((y(es)*)\/n(o)*\)', conn.recbuf):
        res = re.search('\((y(es)*)\/n(o)*\)', conn.recbuf).group(1)
        util.sende(conn, '{}\r'.format(res), expectphrase='password:', timeout=60)
    util.send(conn, '{}\r'.format(userdict['apollo']['password']), expectphrase, 60, regex=True)

    # Compare Apollo hostname to Connected UUT hostname
    log.info(conn.recbuf.strip().split()[0])
    if conn.recbuf.strip().split()[0] != lib.get_hostname():
        lib.cache_data('remote_ts_{}'.format(lib.get_container_name()), conn.recbuf.strip().split()[0])
        log.debug("remote_ts: {}".format(lib.get_cached_data('remote_ts_{}'.format(lib.get_container_name()))))
    else:
        # Reset
        lib.cache_data('remote_ts_{}'.format(lib.get_container_name()), None)

    return True


def enter_remote_server(conn, **kwargs):
    """Enter Remote Apollo server

    To be used when UUT is connected to different/remote Apollo server, i.e. using
    WAN address to connect.

    :param conn: UUT's connection object
    :param kwargs: Required:
            - credentials: User credentials - {'id': username, 'password': password}
                - id : This is the user of the server to do the scp files
                - password: This is the password of the server to do the scp files
    :return:
    """
    username = kwargs['credentials']['id']
    password = kwargs['credentials']['password']

    util.send(conn, '\r', timeout=60)
    if lib.get_cached_data('remote_ts_{}'.format(lib.get_container_name())) not in conn.recbuf:
        # Enter remote server (hostname pulled from MIO container w/check_remote_ts in diag)
        util.sende(conn,
                   'ssh {}@{}\r'.format(username, lib.get_cached_data('remote_ts_{}'.format(lib.get_container_name()))),
                   expectphrase=['(yes/no)', '(y/n)', 'password'],
                   timeout=60,
                   regex=True)
        # Add hostname if needed
        if re.search('\((y(es)*)\/n(o)*\)', conn.recbuf):
            res = re.search('\((y(es)*)\/n(o)*\)', conn.recbuf).group(1)
            util.sende(conn, '{}\r'.format(res), expectphrase='password:', timeout=60, regex=True)
        util.send(conn, '{}\r'.format(password), expectphrase='gen-apollo@.*$', timeout=60, regex=True)
    return


# TODO: Why was this function added again ? Can we not set the time while programming other fields of sprom ?
# If so , add function specific parameter to kwargs
def set_time(conn, idpromcmd, dateoffset, now=datetime.datetime.now(), date_program_format='%m/%d/%y %H:%M:%S',
             skip_fail_pars_list=False):
    """Set time.

    Program Time on BS MIO SPROM

    Sample output:
    ======
    diagmon[0] 1 > cmostime 06/14/16 10:52:37
    Current date & time: 06/14/16  10:52:37
    diagmon[0] 2 >

    :param conn: This is the object connection
    :param idpromcmd: Board to program (bridge/basin)
    :param dateoffset: Date offset at SPROM
    :param now: Actual Date
    :param date_program_format: This is the format to be used to take the format time
    :param skip_fail_pars_list:
    :return:
    """
    log.info('now day: {}'.format(now.day))
    log.info('now month: {}'.format(now.month))
    log.info('now year: {}'.format(now.year))

    date_program_mfg_format = '%m-%d-%y'
    currentdate = now.strftime(date_program_format)
    nowmfg = now.strftime(date_program_mfg_format)
    nowmfg = nowmfg.split('-')
    mfgdate = ''
    for value in nowmfg:
        log.info(' parse data: {}'.format(value))
        mfgdate += "{:02x}".format(int(value))

    log.info('now time: {}'.format(currentdate))
    log.info('mfgtime: {}'.format(mfgdate))
    log.info('idpromcmd: {}'.format(idpromcmd))

    command = "diag mio utils idprom write -d {} -o {} -w {}".format(idpromcmd, dateoffset, mfgdate)
    result = run_functional_test(
        conn=conn,
        test_name='Program Time on SPROM',
        test_command=command,
        skip_fail_pars_list=skip_fail_pars_list
    )

    if result:
        command = "diag mio utils idprom checksum -d {}".format(idpromcmd)
        result = run_functional_test(
            conn=conn,
            test_name='Checksum after set time',
            test_command=command,
            skip_fail_pars_list=skip_fail_pars_list
        )

    return result


def run_led_test(conn, expectphrase=prompt, retry=1, timeout=60, skip_fail_pars_list=False, **kwargs):
    """Run LED test

    :param conn: UUT's connection Object
    :param expectphrase: Phrase expected in response
    :param timeout: Wait time in seconds
    :param retry: Number of retries
    :param skip_fail_pars_list: Flag to catch error phrase. Default- False
    :param kwargs:Required
        :param test_command
        :param led_options
        :param prompt_options
        :param prompt_questions
    :return:
    """
    result = True

    test_cmd = kwargs['test_command']
    options = kwargs['led_options']
    questions = kwargs['prompt_questions']
    answers = kwargs['prompt_options']

    for test in options:
        util.sende(conn=conn,
                   text='{} {}'.format(test_cmd, test),
                   expectphrase=expectphrase,
                   retry=retry,
                   timeout=timeout)
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            error_message = 'Error phrase found'
            log.warning(error_message)
            result = False
        answr = lib.ask_question('{}'.format(questions['test']),
                                 answers='{}'.format(answers['test']))
        if answr not in 'S:s/Y:y' and answr in 'N:n':
            result = False
            util.sende(conn=conn,
                       text='{} {}'.format(test_cmd, 'off'),
                       expectphrase=expectphrase,
                       retry=retry,
                       timeout=timeout)
            break

    return result


def random_led_test(conn,
                    attempts,
                    max_attempts,
                    led_info,
                    led_set,
                    led_color,
                    led_cmd,
                    led_language,
                    prompt_answer,
                    timeout=60,
                    skip_fail_pars_list=False):
    """
    Define random led test to randomly toggle LEDs and allow operator to count.

    """
    userdict = lib.apdicts.userdict
    result = True
    cmd_list = {}

    # Expected Phrase List
    expectphrase = list(prompt)
    expectphrase = expectphrase + ["'Y' or 'N'"]
    log.info(expectphrase)

    # turn off leds
    if not led_off(conn, timeout=timeout, expectphrase=expectphrase):
        result = False
        result_msg = 'Could not turn LEDs off'
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
            resolution_message='Call Support',
        )
        return result

    # construct menush commands for led toggling
    for led in led_set:
        led_type = led_info['port_data'][led]['type']
        led_port = led_info['port_data'][led]['port_num']
        if led_port is not '':
            # construct command string
            if led_type not in cmd_list.keys():
                cmd_list[led_type] = str(led_port)
            else:
                cmd_list[led_type] += (',{}'.format(led_port))
        else:
            cmd_list[led_type] = ''

    for led_type in cmd_list.keys():
        base_cmd = led_cmd['{}_{}'.format(led_type, led_color)]
        cmd_list[led_type] = base_cmd + ' ' + cmd_list[led_type]

    cmd_list = cmd_list.values()
    log.debug('Command list: {}'.format(cmd_list))

    # toggle specified LEDs
    for command in cmd_list:
        util.send(conn, text=command + ' \r', expectphrase=expectphrase, timeout=timeout, regex=True)
        if "'Y' or 'N'" in conn.recbuf:
            util.send(conn,
                      text=' y\r',
                      expectphrase=prompt,
                      timeout=timeout)
        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            result = False
            result_msg = 'LED test command error'
            log.error(result_msg)
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - {}'.format(util.whoami(), result_msg),
                resolution_message='Call Support',
            )
            return result

        # sleep between each command to turn on LEDs
        time.sleep(1)

    # pause before asking operator to count LEDs
    time.sleep(1)

    # ask operator to count LEDs
    try:
        # prompt lock
        lock.initialize_lock_state(name='Prompt lock')
        lock_result, result_msg = lock.acquire_lock(name='Prompt lock')
        if lock_result:
            while True:
                prompt_question = '{}'.format(led_language[led_color + '_question'])
                if attempts <= max_attempts:
                    prompt_question = led_language['attempts'].format(attempts, max_attempts) + ' ' + prompt_question
                else:
                    prompt_question = led_language['warning'] + ' ' + prompt_question
                if attempts > 1:
                    prompt_question = led_language['incorrect'] + ' ' + prompt_question
                # Prompt to check LED status
                led_prompt = lib.ask_question(prompt_question)
                # positive option
                try:
                    led_prompt = int(led_prompt)
                    if led_prompt != prompt_answer:
                        result_msg = 'Incorrect answer {}!'.format(led_prompt)
                        log.error(result_msg)
                        userdict['operator_message'] = util.operator_message(
                            error_message='Error: {} - {}'.format(util.whoami(), result_msg),
                            resolution_message='Call support',
                        )
                        result = False
                        break

                except ValueError:
                    log.warning('Invalid answer "{}" entered! Must be numeric value.'.format(led_prompt))
                    continue
                break

    except apexceptions.ApolloException:
        log.warning('Failure -- Operator prompt expired due to timeout')
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Run LED Test'.format(util.whoami()),
            resolution_message='Call support',
        )

    finally:
        # clean up prompt lock to avoid locking other processes
        lock.release_lock(name='Prompt lock')
        lock.finalize_lock_state(name='Prompt lock')

    return result


def led_off(conn, timeout=30, skip_fail_pars_list=False, expectphrase=prompt):
    """LED off.

    Define led_off to turn ALL LEDs off.
    """
    userdict = lib.apdicts.userdict
    result = True
    cmds = userdict['functional_test']['random_led_test']['cmds']
    log.info('Turning ALL LEDs off!')
    for cmd in cmds.keys():
        if 'off' in cmd:
            util.send(conn,
                      text=cmds[cmd] + ' all\r',
                      expectphrase=expectphrase,
                      timeout=timeout, regex=True)
            if "'Y' or 'N'" in conn.recbuf:
                util.send(conn,
                          text=' y\r',
                          expectphrase=expectphrase,
                          timeout=timeout)
            time.sleep(1)

        # Check for parsing after send
        if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=skip_fail_pars_list):
            result = False
            error_msg = 'Fail to turn all LEDs off'
            log.warning(error_msg)
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - {}'.format(util.whoami(), error_msg),
                resolution_message='Call Support',
            )
            break

    time.sleep(5)
    return result


def blade_verify_ssd_info(conn, retry=0, timeout=1800, skip_fail_pars_list=False, **kwargs):
    """Blade Verify SSD Info

    To make sure that Blade SSD info is correct and also to verify that RAID Array was set correctly

    :param conn: Container Connection
    :param cmd: Command of blade show ssd info
    :param raid_info: (List) Info shown when a RAID Array is set in the UUT
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    cmd = kwargs['cmd']
    raid_info = kwargs['raid_info']
    log.info('Raid info: {}'.format(raid_info))

    # Show SSD Info in recbuf
    if not run_functional_test(
        conn=conn,
        test_name='Verify SSD Info',
        test_command=cmd,
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=timeout,
        retry=retry
    ):
        return False

    # Check RAID Info is in recbuf
    for info in raid_info:
        log.debug('Check disk {}'.format(info))
        if info not in conn.recbuf:
            log.error('RAID "{}" not found.'.format(info))
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - SSD info Not Found'.format(util.whoami()),
                resolution_message='Call Support',
            )
            result = False
            break
        if raid_info[info]:
            log.debug('Check disk size {}'.format(raid_info[info]))
            for line in conn.recbuf.splitlines():
                if 'Disk {}'.format(info) in line:
                    raid_size = str(re.search('Disk .*: (\d*)(\.)*(\d*) GB', line).group(1))
                    if str(raid_info[info]) != raid_size:
                        log.error('RAID Size mismatch. Expected: {}. Recieved: {}'.format(raid_info[info], raid_size))
                        result = False
                        break

    return result


def mio_disk_presence(conn, devices=[], hardware_check=False, expectphrase=prompt,
                      retry=0, timeout=200, skip_fail_pars_list=False):
    """MIO Disk Presence

    This function will execute a Show Inventory Test and evaluate the buffer result to make sure that there is info for
    the specified devices (sda, sdb, sdc, etc)

    :param conn:
    :param devices: List of devices to test (sda, sdb, etc)
    :param hardware_check:
    :param expectphrase:
    :param timeout:
    :param retry:
    :param skip_fail_pars_list:
    :return:
    """
    hardware_check_cnt = 1 if hardware_check else 0
    result = False

    while not result:
        result, hardware_check_cnt = search_for_disk_devices(
            conn=conn,
            hardware_check=hardware_check,
            expectphrase=expectphrase,
            timeout=timeout,
            retry=retry,
            skip_fail_pars_list=skip_fail_pars_list,
            hardware_check_cnt=hardware_check_cnt,
            devices=devices
        )

        # Prompt Message to operator to check the respective hardware
        if hardware_check:
            if hardware_check_cnt <= 0:
                break

            hw_result, hardware_check_cnt = util.check_hardware(hardware_check_cnt, 'Disk and USB Test')

            if not hw_result:
                return False
        else:
            break

    return result


def search_for_disk_devices(conn, hardware_check=False, expectphrase=prompt,
                            timeout=200, retry=0, skip_fail_pars_list=False, **kwargs):
    """Search for Dik Devices

    This function will execute an MIO Disk Test and evaluate the buffer result to make sure that there is info for
    the internal disk and info for the external USB device

    :param conn:
    :param hardware_check:
    :param expectphrase:
    :param timeout:
    :param retry:
    :param skip_fail_pars_list:
    :param kwargs: Required
                    - hardware_check_cnt:
                    - devices: List of devices to test (sda, sdb, etc)
    :return:
    """
    userdict = lib.apdicts.userdict
    hardware_check_cnt = kwargs['hardware_check_cnt']
    devices = kwargs['devices']
    result = True

    hardware_check_count = hardware_check_cnt - 1

    util.sende(conn, 'diag mio show inventory\r', expectphrase=expectphrase, retry=retry, timeout=timeout)

    for device in devices:
        found = False
        for line in conn.recbuf.splitlines():
            log.debug('Line: {}'.format(line))
            log.debug('Found?: {}'.format(found))
            if found:
                if 'Size : NA' in line:
                    found = False
                    log.error('No info found for: {}'.format(device))
                    userdict['operator_message'] = util.operator_message(
                        error_message='Error: {} - No info found for {}'.format(util.whoami(), device),
                        resolution_message='Verify Disk and USB is connected',
                    )
                    hardware_check_count += 1
                    result = False

                break
            if '/DEV/{}'.format(device.upper()) in line:
                found = True
                continue

        if not found:
            break
    log.debug('Res: {}, Cnt: {}'.format(result, hardware_check_count))

    return result, hardware_check_count


def capture_meas(buffer):
    """ Capture Meas tag in menush output

    :buffer - Connection buffer
    """
    for line in buffer.splitlines():
        if 'MEAS:' in line:
            line = line.split(':')
            log.debug('Measurement information: {}'.format(line))
            if 'MEAS' in line[0] and len(line) == 3:
                util.upload_measurement(limit_name='{}'.format(line[1]), capture_value=line[2])
    buffer = buffer.replace('MEAS:', '').strip()
    return buffer
