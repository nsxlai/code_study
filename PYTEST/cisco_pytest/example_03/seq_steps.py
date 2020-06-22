# coding: utf8

import datetime
import time
import logging
import inspect
import sys
import re
import os
import collections
from apollo.engine import apexceptions
from apollo.libs import cesiumlib, lib
from ....lib import util, spark, lock
from ....ssp.env import menush, rommon
from ....ssp.products.baker_street import configuration
from apollo.libs.te_libs.chamber.trunk.chamber_interface import HOT, COLD, AMBIENT, DRY, ChamberInterface

script_path = os.path.dirname(__file__)
log = logging.getLogger(__name__)

# Global
chamber_handler = None

# NOTE: True if want to monitor temperature during test
MONITOR_IN_TEST = True


def mio_seq_block(test_seqs):
    """MIO Sequence Block

    Following is to create MIO Tests Tree

    :param test_seqs: Sequence to add steps
    :return:
    """
    # Initial Board Setup
    mio_tests_seq = test_seqs.add_sequence(name='MIO Tests', precondition="userdict['mio_test']")
    mio_tests_seq.add_step(name='Create Log Directory', function=create_log_directory)
    mio_tests_seq.add_step(name='Init Info', function=init_mio)
    mio_tests_seq.add_step(name='Check Required Files', function=check_required_files)
    boot_rommon_diag_seq_block(mio_tests_seq)

    # FW Upgrades
    upgrade_firmware_seq_block(mio_tests_seq)

    # SPROM Programming
    mio_sprom_seq_block(mio_tests_seq)

    # MAC Address Programming
    mio_mac_seq_block(mio_tests_seq)

    # ACT2 Programming
    mio_act2_seq_block(mio_tests_seq)

    # Functional Testing
    mio_diag_functional_seq_block(mio_tests_seq)
    mio_to_blade_traffic_seq_block(mio_tests_seq)
    mio_tests_seq.add_step(name='Activate Fans for FXOS', function=mio_activate_fans)

    # Clean Up
    mio_final_clean_up(mio_tests_seq)


def mio_init_seq_block(gen_seq):
    """MIO Init Sequence Block

    Following is to create a Sequence that initialize the MIO when a Blade or a NetMod is going to be tested at BS

    :param gen_seq: Sequence to add steps
    :return:
    """
    mio_seq = gen_seq.add_sequence(
        name='MIO Initialization',
        precondition="userdict['mio_config_blades'] or userdict['mio_config_netmods']"
    )
    mio_seq.add_step(name='Create Log Directory', function=create_log_directory)
    mio_seq.add_step(
        name='Gen MGMT IP',
        function=init_chassis,
    )
    mio_seq.add_step(
        name='Check Required Files',
        function=check_required_files,
    )
    boot_rommon_diag_seq_block(
        mio_seq,
        fan_tests=['FAN_SPEED_LEVEL_L5']
    )
    mio_seq.add_step(
        name='Get Blade Images',
        function=get_blade_imgs,
        precondition="userdict['mio_config_blades']"
    )
    mio_seq.add_step(
        name='Init Bridge',
        function=init_bridge_to_blades,
        precondition="userdict['mio_config_blades']"
    )


def blades_seq_block(tests_seqs, voltage='low'):
    """Blades Sequence Block

    Following creates a Test Tree for Blades (PCBP2 and PCB2C)

    :param tests_seqs: Sequence to add steps
    :param voltage: low/high This parameter is used at PCB2C, to set Test voltage
    :return:
    """
    # Initial Board Setup
    blade_tests_seq = tests_seqs.add_sequence(name='Blade Tests', precondition="userdict['blade_test']")
    blade_tests_seq.add_step(name='MIO Init Status', function=mio_init_status)
    blade_tests_seq.add_step(name='Init Info', function=init_blades)
    blade_tests_seq.add_step(name='Open Connection', function=open_connection)
    blade_tests_seq.add_step(name='Enter MIO', function=ssh_enter_menu)
    blade_tests_seq.add_step(name='CD Test Directory', function=cd_test_dir)
    # -----Set Test Voltage for PCB2C (High/Low)-----
    blade_tests_seq.add_step(
        name='Set Voltage {}'.format(voltage),
        function=functional_test,
        precondition="userdict['area'] == 'PCB2C'",
        kwargs={'test_name': 'voltage {}'.format(voltage), 'module': True}
    )
    blade_tests_seq.add_step(
        name='Fetch Date Time',
        function=get_time,
        kwargs={'date_format': '%m/%d/%y', 'seperator': '/'},
        precondition="'PCBP2' in userdict['area']"
    )

    # FW Upgrades
    blade_upgrade_seq_block(blade_tests_seq)

    # SPROM Programming
    blade_tests_seq.add_step(
        name='Check SN',
        function=verify_blade_sn,
        precondition="userdict['area'] == 'PCBP2'"
    )
    blade_sprom_seq_block(blade_tests_seq)

    # MAC Address Programming
    blade_program_mac_seq_block(blade_tests_seq)

    # ACT2 Programming
    blade_act2_seq_block(blade_tests_seq)

    # Functional Testing
    blade_voltage_test_seq_block(blade_tests_seq)
    bmc_tests_seq_block(blade_tests_seq)
    efi_tests_seq_block(blade_tests_seq)
    blade_tests_seq.add_step(
        name='Reboot',
        function=functional_test,
        kwargs={'test_name': 'reboot blade', 'module': True}
    )
    blade_tests_seq.add_step(
        name='Cruz Upgrade',
        function=upgrade_bios,
        kwargs={'upg': 'cruzupg'}
    )
    blade_tests_seq.add_step(
        name='Verify Cruz',
        function=functional_test,
        kwargs={'test_name': 'cruz ver', 'module': True},
    )
    blade_tests_seq.add_step(
        name='LSI Upgrade CUS',
        function=upgrade_bios,
        kwargs={'upg': 'lsiupgcus'}
    )
    blade_tests_seq.add_step(
        name='Reboot After Upgrade',
        function=functional_test,
        kwargs={'test_name': 'reboot blade', 'module': True}
    )
    # TODO; temporarily comment out
    # sub_seq.add_step(
    #     name='Verify LSI',
    #     function=functional_test,
    #     kwargs={'test_name': 'lsi ver', 'module': True},
    # )
    hostdiag_tests_seq_block(blade_tests_seq)
    blade_tests_seq.add_step(
        name='Verify RAID Array',
        function=blade_verify_ssd_info,
    )
    blade_tests_seq.add_step(
        name='Verify ACT2',
        function=verify_blade_act2,
        kwargs={'fail_if_not_installed': True, 'skip_fail_pars_list': True}
    )
    # -----Return Test Voltage to Normal (for PCB2C Only)-----
    blade_tests_seq.add_step(
        name='Set Voltage Normal',
        function=functional_test,
        precondition="userdict['area'] == 'PCB2C'",
        kwargs={'test_name': 'voltage normal', 'module': True}
    )
    # Please make sure to include the 3 JPEG files in /opt/cisco/te/media folder for this test
    blade_tests_seq.add_step(
        name='LED Test',
        function=blade_led_test,
        precondition="userdict['area'] == 'PCBP2'",
        kwargs={'led_colors': ['amber', 'green']}
    )
    blade_tests_seq.add_step(
        name='LED Blade Locator Test',
        precondition="userdict['area'] == 'PCBP2'",
        function=blade_led_locator_test
    )
    blade_tests_seq.add_step(
        name='Final Clean Up',
        function=functional_test,
        kwargs={'test_name': 'bmc cleanup', 'module': True}
    )


# region MIO P2C
def boot_rommon_seq_block(seq, reboot=True):
    """Boot Rommon

     This sequence will boot a unit to Rommon

    :param seq:
    :param reboot: If true, the Chassis will be rebooted (With its PS)
    :return:
    """
    boot_rommon_seq = seq.add_sequence(name='Boot Rommon')
    boot_rommon_seq.add_step(name='Boot Rommon', function=boot_rommon, kwargs={'reboot': reboot})
    boot_rommon_seq.add_step(name='Set settings', function=set_settings_rommon)
    boot_rommon_seq.add_step(name='Check Network', function=check_network_rommon, kwargs={'hardware_check': True})


def boot_diag_seq_block(seq):
    """Boot Diag

    This sequence boots a unit from Rommon to Diag

    :param seq:
    :return:
    """
    diag_init = seq.add_sequence(name='Boot Diag')
    diag_init.add_step(name='Boot diag', function=boot_diag, kwargs={'skip_fail_pars_list': True})
    diag_init.add_step(name='Set MAC mgmt', function=set_mac_menush, kwargs={'module': 'mgmt'})
    diag_init.add_step(name='Set Network mgmt', function=set_network_menush, kwargs={'module': 'mgmt'})
    diag_init.add_step(name='Check Network from diag', function=check_network_menush)


def boot_rommon_diag_seq_block(seq, voltages=['Normal'], boards=['Basin', 'System'],
                               fan_tests=['FAN_SPEED_LEVEL_L5'], reboot=True):
    """Boot Rommon and Diag

    This sequence will boot a unit to Rommon and then to Diag

    :param seq:
    :param voltages: List of Voltages to test (High, Low, Normal)
    :param boards: List of boards to check (System, Croxley, Basin)
    :param fan_tests: List of fan tests to perform
    :param reboot:
    :return:
    """
    boot_diag_seq = seq.add_sequence(name='Boot Rommon and Diag')
    boot_rommon_seq_block(boot_diag_seq, reboot)
    boot_diag_seq.add_step(name='Show Info', function=show_info_in_rommon)
    boot_diag_seq.add_step(name='Show NVRam', function=show_nvram_in_rommon)
    boot_diag_seq_block(boot_diag_seq)
    boot_diag_seq.add_step(name='Install Patches', function=install_blade_patches)
    boot_diag_seq.add_step(
        name='Show Inventory',
        function=show_inventory_in_menush,
    )
    mio_voltage_seq_block(boot_diag_seq, voltages, boards)
    boot_diag_seq.add_step(
        name='Fan test',
        function=fan_test,
        kwargs={'tests': fan_tests, 'skip_fail_pars_list': True}
    )


def mio_voltage_seq_block(seq, voltages=['Normal'], boards=['Basin', 'System']):
    """MIO Voltage

    As TDE, will need a function to test MIO Voltages

    :param seq:
    :param voltages: List of Voltages to test (High, Low, Normal)
    :param boards: List of boards to check (System, Croxley, Basin)
    :return:
    """
    voltage_test_seq = seq.add_sequence(name='Voltage Tests')
    for board in boards:
        for voltage in voltages:
            voltage_test_seq.add_step(
                name='Set and Check {} {} Voltage'.format(board, voltage),
                function=functional_test,
                kwargs={'test_name': 'Set {} Voltage {}'.format(board, voltage)}
            )


def reinsert_epms_seq_block(seq):
    """Reinsert EPMs

    This function will reboot a unit and then try to detect again the EPMs

    :param seq:
    :return:
    """
    reinsert_epms = seq.add_sequence(
        name='Reinsert EPMs',
        precondition="userdict['control_step']['reinsert_epms']"
    )
    boot_rommon_diag_seq_block(reinsert_epms)
    reinsert_epms.add_step(name='Detect EPMs after reinsert', function=detect_epms)


def upgrade_firmware_seq_block(seq, enabled=True):
    """Upgrade Firmware

    This function will add all Firmware Upgrade sequence to MIO Test Sequence

    :param seq:
    :param enabled:
    :return:
    """
    programmable_seq = seq.add_sequence(name='Verify and Upgrade Programmables', enabled=enabled)
    programmable_seq.add_step(name='Format MSATA', function=functional_test, kwargs={'test_name': 'format bootflash'})
    boot_rommon_seq_block(programmable_seq, reboot=True)
    boot_diag_seq_block(programmable_seq)
    programmable_seq.add_step(
        name='Check Firmware Version - Rommon',
        function=check_firmware_version,
        kwargs={'environment': 'rommon', 'firmwares': ['ROMMON', 'Bridge-FPGA']}
    )
    rommon_upgrade_seq_block(programmable_seq)
    bridge_fpga_upgrade_seq_block(programmable_seq)
    programmable_seq.add_step(name='Show Inventory', function=show_inventory_in_menush)
    programmable_seq.add_step(
        name='Check Firmware Version - Menush',
        function=check_firmware_version,
        kwargs={'environment': 'menush', 'firmwares': ['Bridge PSEQ', 'Basin FPGA', 'Basin M3']}
    )
    bridge_pseq_upgrade_seq_block(programmable_seq)
    basin_pseq_upgrade_seq_block(programmable_seq)
    basin_fpga_upgrade_seq_block(programmable_seq)


def rommon_upgrade_seq_block(seq, force=False):
    """Rommon Upgrade

    :param seq:
    :param force:
    :return:
    """
    seq.add_step(name='Force Upgrade - Rommon upgrade', function=force_upgrade, kwargs={'force_upgrade': force})
    rommon_upgrade = seq.add_sequence(
        name='Rommon Upgrade',
        iterations=(lib.ITERATION_QTY, 2),
        precondition="userdict['control_step']['update_rommon'] or userdict['force_upgrade']")
    # TODO:Remove skip_fail_pars_list
    rommon_upgrade.add_step(
        name='Rommon Upgrade',
        function=update_rommon_in_menush,
        kwargs={'skip_fail_pars_list': True}
    )
    boot_rommon_diag_seq_block(rommon_upgrade, reboot=False)
    rommon_upgrade.add_step(
        name='Check Rommon Version',
        function=check_firmware_version,
        kwargs={'environment': 'rommon', 'firmwares': ['ROMMON']}
    )


def bridge_fpga_upgrade_seq_block(seq, force=False):
    """Bridge FPGA Upgrade

    :param seq:
    :param force:
    :return:
    """
    seq.add_step(name='Force Upgrade - Bridge FPGA', function=force_upgrade, kwargs={'force_upgrade': force})
    bridge_fpga_upgrade = seq.add_sequence(
        name='Bridge FPGA Upgrade',
        precondition="userdict['control_step']['update_bridge-fpga'] or userdict['force_upgrade']"
    )
    bridge_fpga_upgrade.add_step(name='Bridge FPGA Upgrade', function=update_fpga_in_menush)
    boot_rommon_diag_seq_block(bridge_fpga_upgrade)
    bridge_fpga_upgrade.add_step(
        name='Check Bridge FPGA Upgrade',
        function=check_firmware_version,
        kwargs={'environment': 'rommon', 'firmwares': ['Bridge-FPGA']}
    )


def bridge_pseq_upgrade_seq_block(seq, force=False):
    """Bridge PSEQ Upgrade

    :param seq:
    :param force:
    :return:
    """
    seq.add_step(name='Force Upgrade - Bridge PSEQ', function=force_upgrade, kwargs={'force_upgrade': force})
    bridge_pseq_upgrade = seq.add_sequence(
        name='Bridge PSEQ Upgrade',
        precondition="userdict['control_step']['update_bridge pseq'] or userdict['force_upgrade']"
    )
    bridge_pseq_upgrade.add_step(name='Bridge PSEQ Upgrade', function=update_pseq_in_menush)
    boot_rommon_diag_seq_block(bridge_pseq_upgrade)
    bridge_pseq_upgrade.add_step(
        name='Check Bridge PSEQ Upgrade',
        function=check_firmware_version,
        kwargs={'environment': 'menush', 'firmwares': ['Bridge PSEQ']}
    )


def basin_fpga_upgrade_seq_block(seq, force=False):
    """Basin FPGA Upgrade

    :param seq:
    :param force:
    :return:
    """
    seq.add_step(name='Force Upgrade - Basin FPGA', function=force_upgrade, kwargs={'force_upgrade': force})
    basin_fpga_upgrade = seq.add_sequence(
        name='Basin FPGA Upgrade',
        precondition="userdict['control_step']['update_basin fpga'] or userdict['force_upgrade']"
    )
    basin_fpga_upgrade.add_step(name='Basin FPGA Upgrade', function=update_fpga_basin_in_menush)
    boot_seq = basin_fpga_upgrade.add_sequence(
        name="Reboot",
        precondition="not userdict['control_step']['update_basin m3'] "
                     "and not userdict['control_step']['update_basin fpga']"
    )
    boot_rommon_diag_seq_block(boot_seq)
    basin_fpga_upgrade.add_step(
        name='Check Basin FPGA Upgrade',
        function=check_firmware_version,
        kwargs={'environment': 'menush', 'firmwares': ['Basin FPGA']}
    )


def basin_pseq_upgrade_seq_block(seq, force=False):
    """Basin PSEQ Upgrade

    :param seq:
    :param force:
    :return:
    """
    seq.add_step(name='Force Upgrade - Basin PSEQ', function=force_upgrade, kwargs={'force_upgrade': force})
    basin_pseq_upgrade = seq.add_sequence(
        name='Basin PSEQ Upgrade',
        precondition="userdict['control_step']['update_basin m3'] or userdict['force_upgrade']"
    )
    basin_pseq_upgrade.add_step(name='Basin PSEQ Upgrade', function=update_pseq_basin_in_menush)
    boot_seq = basin_pseq_upgrade.add_sequence(
        name='Reboot',
        precondition="not userdict['control_step']['update_basin m3'] "
                     "and not userdict['control_step']['update_basin fpga']"
    )
    boot_rommon_diag_seq_block(boot_seq)
    basin_pseq_upgrade.add_step(
        name='Check Basin PSEQ Upgrade',
        function=check_firmware_version,
        kwargs={'environment': 'menush', 'firmwares': ['Basin M3']}
    )


def force_upgrade(force_upgrade=False):
    """Force upgrade.

    As TDE, will define force_upgrade so that test can initialize upgrade.
    """

    userdict = lib.apdicts.userdict
    userdict['force_upgrade'] = force_upgrade
    if force_upgrade:
        log.info('------------------')
        log.info('Forcing Upgrade')
        log.info('------------------')

    return lib.PASS


def blades_power_all(blades=[], action='off', retry=0, timeout=500, skip_fail_pars_list=False, skip_fail=False):
    """Blades Power All

    Power Off/On specified Blades

    :param blades: A List of strings that indicates which Blade must be powered off (e.g. ['1', '2', '3'])
    :param action:  (String) 'on' or 'off'
    :param retry:
    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    for blade_no in blades:
        userdict['module_no'] = blade_no
        if lib.PASS != functional_test(
            test_name='blade {}'.format(action),
            module=True,
            timeout=timeout,
            retry=retry,
            skip_fail=skip_fail,
            skip_fail_pars_list=skip_fail_pars_list
        ):
            return lib.FAIL
        util.sleep(5)

    return lib.PASS


def mio_sprom_seq_block(seq):
    """MIO SPROM

    This function will add all SPROM Tests to MIO Tests Tree

    :param seq:
    :return:
    """
    sprom_seq = seq.add_sequence(name='SPROM Testing')
    sprom_seq.add_step(name='Program RTC', function=program_rtc)
    boot_rommon_diag_seq_block(sprom_seq)
    sprom_seq.add_step(name='Verify RTC', function=verify_rtc)
    sprom_seq.add_step(name='Check SN', function=verify_mio_sn)
    sprom_seq.add_step(name='Program Date Time', function=set_time)
    sprom_seq.add_step(
        name='Get Basin IDPROM Values',
        function=mio_get_idprom_values,
        kwargs={'board': 'basin'}
    )
    sprom_seq.add_step(
        name='Verify Basin CMPD',
        function=mio_verify_sprom,
        kwargs={'board': 'basin'}
    )
    sprom_seq.add_step(
        name='Verify Basin Test Records',
        function=mio_verify_sprom_to_tst,
        kwargs={'board': 'basin'}
    )
    sprom_seq.add_step(
        name='Get Bridge IDPROM Values',
        function=mio_get_idprom_values,
        kwargs={'board': 'bridge'}
    )
    sprom_seq.add_step(
        name='Verify Bridge CMPD',
        function=mio_verify_sprom,
        kwargs={'board': 'bridge'}
    )
    sprom_seq.add_step(
        name='Verify Bridge Test Records',
        function=mio_verify_sprom_to_tst,
        kwargs={'board': 'bridge'}
    )


def mio_mac_seq_block(seq):
    mac_seq = seq.add_sequence(name='Bridge MAC')
    mac_seq.add_step(
        name='Fetch MAC',
        function=mio_fetch_mac
    )
    mac_seq.add_step(
        name='Verify MAC',
        function=verify_mac
    )
    mac_seq.add_step(
        name='Program MAC',
        function=mio_program_mac,
        precondition="userdict['control_step']['program_mac']"
    )


def mio_act2_seq_block(seq, module=False, certs=['rsa', 'harsa']):
    """MIO ACT2

    This Function will add all ACT2 Sequence to a MIO (or NetMod) Tests Tree

    :param seq:
    :param module: If true, then the ACT2 will try to be installed in a NetMod
    :param certs: A list of certs to verify and Install (By Defaulr rsa and harsa)
    :return:
    """
    act2_seq = seq.add_sequence(name='ACT2 Installation')
    act2_seq.add_step(
        name='Verify ACT2 Status',
        function=mio_verify_act2,
        kwargs={'module': module, 'certs': certs}
    )
    act2_seq.add_step(
        name='Program ACT2',
        function=mio_program_act2,
        kwargs={'module': module, 'certs': certs},
        precondition="userdict['program_act2']"
    )
    act2_seq.add_step(
        name='Verify ACT2 After Install',
        function=mio_verify_act2,
        kwargs={'module': module, 'certs': certs, 'fail_if_not_installed': True},
        precondition="userdict['program_act2']"
    )


def mio_program_act2(module=False, certs=['rsa', 'harsa'], retry_cnt=0,
                     timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """Program Act2

    As TDE, will provide way to program uut with Act2 authentication to qualify authentic cisco products

    :param module: Just if a unit is a NetMode, set it to True
    :param certs: A list of Certs to be programmed
    :param retry_cnt:
    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict

    retry_powercycle = 3
    retry = 0

    modulecmd = 'e{} '.format(userdict['module_no']) if module else ''

    while retry < retry_powercycle:
        result = menush.program_act2(
            conn=userdict['conn'],
            certs=certs,
            act2_options=userdict['act2_menu_cmds'],
            modulecmd=modulecmd,
            skip_fail_pars_list=skip_fail_pars_list,
            retry=retry_cnt,
            timeout=timeout
        )
        if result:
            break
        else:
            log.warning('ACT2 Program failed.')
            retry += 1
            log.info('Rebooting to retry programming!')
            log.info('Retry {} of {}'.format(retry, retry_powercycle))
            # power cycle and boot diag
            boot_rommon(reboot=True)
            set_settings_rommon()
            check_network_rommon(hardware_check=True)
            boot_diag(skip_fail_pars_list=True)
            set_network_menush(module='mgmt')
            check_network_menush()

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Program ACT2 Failed'.format(util.whoami()),
            resolution_message='Call support',
        )
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_diag_functional_seq_block(seq):
    """MIO Diag Functional Sequence Block

    This function will add all Functional Tests to an MIO Tests Tree

    * Start and Stop Heatsink are preconditioned to run only at PCBP2,
    we need to ensure that we have 100% fan speed at 2C

    :param seq:
    :return:
    """
    functional_seq = seq.add_sequence(name='Functional Testing')
    functional_seq.add_step(name='Verify EPMs', function=detect_epms)
    reinsert_epms_seq_block(functional_seq)
    functional_seq.add_step(
        name='i2c Communication',
        function=functional_test,
        kwargs={'test_name': 'i2c Communication', 'hardware_check': True}
    )
    functional_seq.add_step(
        name='Fan test',
        function=fan_test,
        kwargs={'tests': ['FAN_SPEED_LEVEL_L1', 'FAN_SPEED_LEVEL_L5', 'FAN_SPEED_LEVEL_L1'],
                'skip_fail_pars_list': True}
    )
    functional_seq.add_step(name='Read Temperature', function=read_temperature)
    functional_seq.add_step(
        name='Power Redundancy',
        function=power_redundancy,
        precondition="userdict['area'] == 'PCBP2'"
    )
    functional_seq.add_step(
        name='Start Heatsink',
        function=fan_test,
        kwargs={'tests': ['FAN_SPEED_LEVEL_L2'], 'skip_fail_pars_list': True},
        precondition="userdict['area'] == 'PCBP2'"
    )
    functional_seq.add_step(
        name='Disk and USB Presence',
        function=mio_disk_presence,
        kwargs={'devices': ['sda', 'sdb'], 'hardware_check': True}
    )
    functional_seq.add_step(
        name='Disk Test',
        function=functional_test,
        kwargs={'test_name': 'disk test', 'skip_fail_pars_list': True, 'hardware_check': True}
    )
    functional_seq.add_step(
        name='PCI Check',
        function=functional_test,
        kwargs={'test_name': 'pci test'}
    )
    functional_seq.add_step(
        name='MIO External Traffic',
        function=functional_test,
        kwargs={'test_name': 'mio external', 'timeout': 500, 'hardware_check': True},
        enabled=True
    )
    functional_seq.add_step(
        name='EPM2 Internal Traffic',
        function=functional_test,
        kwargs={'test_name': 'epm2 internal'},
        enabled=True
    )
    functional_seq.add_step(
        name='EPM3 Internal Traffic',
        function=functional_test,
        kwargs={'test_name': 'epm3 internal'},
        enabled=True
    )
    functional_seq.add_step(
        name='Read Heatsink Temperature',
        function=read_temperature,
        precondition="userdict['area'] == 'PCBP2'"
    )
    functional_seq.add_step(
        name='Stop Heatsink',
        function=fan_test,
        kwargs={'tests': ['FAN_SPEED_LEVEL_L1'], 'skip_fail_pars_list': True},
        precondition="userdict['area'] == 'PCBP2'"
    )
    functional_seq.add_step(name='Capture system info', function=capture_system_info)
    functional_seq.add_step(
        name='Memory Test',
        function=memory_test,
        kwargs={'test_name': 'memory test'}
    )
    functional_seq.add_step(
        name='OBFL Test',
        function=functional_test,
        kwargs={'test_name': 'obfl test'}
    )
    functional_seq.add_step(name='OBFL Erase', function=obfl_erase)
    functional_seq.add_step(
        name='NVRam Test',
        function=functional_test,
        kwargs={'test_name': 'nvram test'}
    )
    functional_seq.add_step(
        name='Verify ACT2 Status',
        function=mio_verify_act2,
        kwargs={'fail_if_not_installed': True, 'certs': ['rsa', 'harsa']}
    )
    functional_seq.add_step(
        name='Format MSATA',
        function=functional_test,
        kwargs={'test_name': 'format bootflash'}
    )


def mio_to_blade_traffic_seq_block(seq):
    """MIO to Blade Traffic

    Test Traffic from MIO through blades

    :param seq:
    :return:
    """
    mio_to_blade = seq.add_sequence(name='MIO to Blade Traffic')
    mio_to_blade.add_step(
        name='Get Blade Images',
        function=get_blade_imgs
    )
    mio_to_blade.add_step(
        name='Init Bridge',
        function=init_bridge_to_blades
    )
    mio_to_blade.add_step(
        name='MIO to Blade1 Traffic',
        function=functional_test,
        kwargs={'test_name': 'cruztraffic blade1', 'timeout': 900}
    )
    mio_to_blade.add_step(
        name='MIO to Blade2 Traffic',
        function=functional_test,
        kwargs={'test_name': 'cruztraffic blade2', 'timeout': 900}
    )
    mio_to_blade.add_step(
        name='MIO to Blade3 Traffic',
        function=functional_test,
        kwargs={'test_name': 'cruztraffic blade3', 'timeout': 900}
    )


def mio_final_clean_up(seq, reboot=True):
    """MIO Final Clean Up.

    As TDE, will define clear_settings_in_rommon so that clear settings.

    :param seq:
    :param reboot:
    :return:
    """
    clear_seq = seq.add_sequence(name='Final Clean Up')
    clear_seq.add_step(
        name='NVRam Erase',
        function=functional_test,
        kwargs={'test_name': 'nvram erase'}
    )
    clear_seq.add_step(
        name='Boot Rommon',
        function=boot_rommon,
        kwargs={'reboot': reboot, 'skip_fail_pars_list': True}
    )
    clear_seq.add_step(
        name='Clear settings',
        function=clear_settings_rommon
    )
# endregion


def blade_upgrade_seq_block(seq):
    """Blade Upgrades Sequence

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(
        name='Firmware Upgrade',
    )
    sub_seq.add_step(
        name='BMC Upgrade',
        function=upgrade_bios,
        kwargs={'upg': 'bmcupg'},
    )
    sub_seq.add_step(  # CPLD UPG does not require PID option. Safe to do this UPG without PID option first
        name='CPLD Upgrade',
        function=functional_test,
        kwargs={'test_name': 'cpld upg', 'module': True},
    )
    sub_seq.add_step(
        name='Verify BMC Version',
        function=functional_test,
        kwargs={'test_name': 'bmc ver', 'module': True},
    )
    sub_seq.add_step(
        name='P4 Upgrade',
        function=functional_test,
        kwargs={'test_name': 'p4 upg', 'module': True},
    )
    sub_seq.add_step(
        name='P9 Upgrade',
        function=functional_test,
        kwargs={'test_name': 'p9 upg', 'module': True},
    )
    sub_seq.add_step(
        name='PSOC Upgrade',
        function=functional_test,
        kwargs={'test_name': 'psoc upg', 'module': True},
    )
    sub_seq.add_step(
        name='VR13 Upgrade',
        function=functional_test,
        kwargs={'test_name': 'vr13 upg', 'module': True},
    )
    sub_seq.add_step(
        name='Bios Upgrade',
        function=upgrade_bios,
        kwargs={'upg': 'biosupg'},
    )
    sub_seq.add_step(
        name='Verify BIOS Version',
        function=functional_test,
        kwargs={'test_name': 'bios ver', 'module': True}
    )


def blade_sprom_seq_block(seq):
    """Blade SPROM Sequence

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(name='Program IDPROM')
    sub_seq.add_step(name='CMPD Fetch', function=fetch_cmpd_sprom)
    sub_seq.add_step(
        name='Program IDPROM',
        function=program_bmc,
        precondition="userdict['area'] == 'PCBP2'"
    )
    sub_seq.add_step(
        name='Get IDPROM Values',
        function=get_blade_idprom_values
    )
    sub_seq.add_step(name='CMPD Verify', function=cmpd_verify_blade)


def blade_act2_seq_block(seq):
    """Blade ACT2 Sequence

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(name='ACT2')
    sub_seq.add_step(
        name='Verify ACT2 Status',
        function=verify_blade_act2,
        kwargs={'skip_fail_pars_list': True}
    )
    sub_seq.add_step(
        name='Install ACT2',
        function=blade_program_act2,
        kwargs={'skip_fail_pars_list': True},
        precondition="userdict['program_act2'] and userdict['area'] == 'PCBP2'"
    )
    sub_seq.add_step(
        name='Reboot',
        function=functional_test,
        kwargs={'test_name': 'reboot blade', 'module': True, 'timeout': 420},
        precondition="userdict['program_act2'] and userdict['area'] == 'PCBP2'"
    )
    # TODO Check if following is required
    sub_seq.add_step(
        name='MCClient',
        function=mcclient,
        kwargs={'skip_fail_pars_list': True},
        precondition="userdict['program_act2'] and userdict['area'] == 'PCBP2'"
    )


def blade_program_mac_seq_block(seq):
    """Program Blade ACT2 MAC Addresses

    :param seq:
    :return:
    """
    boards = {'bmc': 'bld', 'mezz': 'mezz', 'mlom': 'mlom'}
    sub_seq = seq.add_sequence(name='Program MAC Addresses', enabled=True)
    for board in boards:
        mac_seq = sub_seq.add_sequence(name='{} MAC'.format(board.upper()))
        mac_seq.add_step(
            name='Fetch MAC',
            function=blade_fetch_mac,
            kwargs={'board': board, 'idprom_cmd': boards[board]}
        )
        mac_seq.add_step(
            name='Verify MAC',
            function=verify_mac,
            kwargs={'board': board}
        )
        mac_seq.add_step(
            name='Program MAC',
            function=blade_program_mac,
            kwargs={'board': board},
            precondition="userdict['control_step']['program_mac'] and userdict['area'] == 'PCBP2'"
        )


def blade_voltage_test_seq_block(seq, voltages=['high', 'low', 'normal']):
    sub_seq = seq.add_sequence(name='Blade Voltage Tests',
                               precondition="userdict['area'] == 'PCBP2' or userdict['area'] == 'DBGPCB'")
    for voltage in voltages:
        sub_seq.add_step(
            name='Voltage {}'.format(voltage),
            function=functional_test,
            kwargs={'test_name': 'voltage {}'.format(voltage), 'module': True}
        )


def bmc_tests_seq_block(seq):
    """Blades BMC Functional Tests

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(name='BMC Tests')
    sub_seq.add_step(
        name='BMC Clean Up Before Test',
        function=functional_test,
        kwargs={'test_name': 'bmc cleanup', 'module': True}
    )
    sub_seq.add_step(
        name='BMC OffAll',
        function=functional_test,
        kwargs={'test_name': 'bmc offall', 'module': True}
    )
    sub_seq.add_step(
        name='BMC OnAll',
        function=functional_test,
        kwargs={'test_name': 'bmc onall', 'module': True}
    )
    sub_seq.add_step(
        name='Set Date',
        function=set_date
    )
    sub_seq.add_step(
        name='Verify Temp',
        function=functional_test,
        kwargs={'test_name': 'verify temp', 'module': True}
    )
    sub_seq.add_step(
        name='Verify CPU',
        function=functional_test,
        kwargs={'test_name': 'verify cpu', 'module': True}
    )
    sub_seq.add_step(
        name='BMC PX889X_Marg',
        function=functional_test,
        kwargs={'test_name': 'bmc px889x', 'module': True}
    )
    sub_seq.add_step(
        name='Verify SSD Presence',
        function=functional_test,
        kwargs={'test_name': 'verify ssd', 'module': True}
    )
    sub_seq.add_step(
        name='BMC sBoot',
        function=functional_test,
        kwargs={'test_name': 'bmc sboot', 'module': True}
    )
    sub_seq.add_step(
        name='BMC IP miDimm',
        function=functional_test,
        kwargs={'test_name': 'bmc ipmidimm', 'module': True}
    )
    sub_seq.add_step(
        name='BMC System Check',
        function=functional_test,
        kwargs={'test_name': 'bmc sys chk', 'module': True}
    )
    sub_seq.add_step(
        name='BMC Memory Check',
        function=functional_test,
        kwargs={'test_name': 'bmc mmry chk', 'module': True, 'skip_fail_pars_list': True},
    # TODO; raylai; review the need for implement BMC memory check in DBGPCB P2C loop
    #     precondition='\'DBGPCB\' not in userdict[\'area\']'
    )
    sub_seq.add_step(
        name='BMC MP Check',
        function=functional_test,
        kwargs={'test_name': 'bmc mp chk', 'module': True}
    )
    sub_seq.add_step(
        name='BMC IP miCMD',
        function=functional_test,
        kwargs={'test_name': 'bmc ipmicmd', 'module': True}
    )
    sub_seq.add_step(
        name='BMC Power Check',
        function=functional_test,
        kwargs={'test_name': 'bmc powerchk', 'module': True}
    )
    sub_seq.add_step(
        name='BMC Dimm Channel',
        function=functional_test,
        kwargs={'test_name': 'bmc dimm channel', 'module': True}
    )
    sub_seq.add_step(
        name='BMC Dimm Status',
        function=functional_test,
        kwargs={'test_name': 'bmc dimm status', 'module': True}
    )


def efi_tests_seq_block(seq):
    """Blades EFI Functional Tests

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(name='EFI Tests')
    sub_seq.add_step(
        name='Blade Bifurcation',
        function=functional_test,
        kwargs={'test_name': 'blade bifurcation', 'module': True}
    )
    sub_seq.add_step(
        name='EFI LPC Test',
        function=functional_test,
        kwargs={'test_name': 'efi lpc test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI PCI Test',
        function=functional_test,
        kwargs={'test_name': 'efi pci test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI Cache Test',
        function=functional_test,
        kwargs={'test_name': 'efi cache test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI Graphic Test',
        function=functional_test,
        kwargs={'test_name': 'efi gphc test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI Memory Test',
        function=functional_test,
        kwargs={'test_name': 'efi mmry test', 'module': True, 'timeout': 1800}
    )
    sub_seq.add_step(
        name='EFI QPI Test',
        function=functional_test,
        kwargs={'test_name': 'efi qpi test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI CPU Test',
        function=functional_test,
        kwargs={'test_name': 'efi cpu test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI IIO Test',
        function=functional_test,
        kwargs={'test_name': 'efi iio test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI PCH Test',
        function=functional_test,
        kwargs={'test_name': 'efi pch test', 'module': True}
    )
    sub_seq.add_step(
        name='EFI USB Test',
        function=functional_test,
        kwargs={'test_name': 'efi usb test', 'module': True}
    )


def hostdiag_tests_seq_block(seq):
    """Blades HostDiag Functional Tests

    :param seq:
    :return:
    """
    sub_seq = seq.add_sequence(name='HostDiag Tests')
    sub_seq.add_step(
        name='HostDiag Bios Ver Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag biosver chk', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag System Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag sys chk', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Nitrox Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag nitrox test', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Stress Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag stress test', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Cruz Traffic',
        function=functional_test,
        kwargs={'test_name': 'hostdiag cruz traffic', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Cruz Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag cruz test', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Memory Check',
        function=functional_test,
        kwargs={'test_name': 'hostdiag mmry chk', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag PMem2 Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag pmem2 test', 'module': True, 'timeout': 1200}
    )
    # The 3 minutes timer separation between PMem2 and CPUtemptest will allow the CPU to cool down between each test
    # The higher CPU model in Olympia and Knightsbridge will overheat if there is no sufficient wait time in between
    sub_seq.add_step(
        name='Hostdiag 3 Min Timer',
        function=test_timer,
        kwargs={'seconds': 180},
        precondition="userdict['area'] == 'PCB2C'"
    )
    sub_seq.add_step(
        name='HostDiag CPU Temp Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag cpu temp', 'module': True}
    )
    sub_seq.add_step(
        name='Clean Partitions',
        function=functional_test,
        kwargs={'test_name': 'clean partition', 'module': True}
    )
    sub_seq.add_step(
        name='HostDiag Disk Test',
        function=functional_test,
        kwargs={'test_name': 'hostdiag disk test', 'module': True, 'skip_fail_pars_list': True}
    )


def test_timer(seconds):
    """
    Test step for adding delays between test steps
    :param seconds: Specify how many seconds to wait/sleep/delay between test steps
    :return:
    """
    util.sleep(seconds)
    return lib.PASS


# region -----------------------------Diag sequences---------------------------
def boot_diag(img_loc='tftp', retry_cnt=1, timeout=300, skip_fail=False, skip_fail_pars_list=False):
    """Boot diag.

    As TDE, will boot provided diags images from rommon env to move into diags testing
    """
    userdict = lib.apdicts.userdict
    expectphrase = ['activate this console']

    result = menush.boot(
        conn=userdict['conn'],
        cmd='{}:{}'.format(img_loc, userdict['diag_image']),
        expectphrase=expectphrase,
        retry=retry_cnt,
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def set_mac_menush(module, retry=0, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """Set Mac Menush

    As TDE, will configure dummy mac settings to allow connection of uut to private Network
    """
    userdict = lib.apdicts.userdict

    result = menush.set_mac(
        conn=userdict['conn'],
        timeout=timeout,
        retry=retry,
        skip_fail_pars_list=skip_fail_pars_list,
        module=module,
        mac=userdict['mac']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def set_network_menush(module, retry=0, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """Set Network Menush

    As TDE, will configure network settings to allow connection of uut to private Network
    """
    userdict = lib.apdicts.userdict

    result = menush.set_network(
        conn=userdict['conn'],
        timeout=timeout,
        retry=retry,
        skip_fail_pars_list=skip_fail_pars_list,
        module=module,
        ip=userdict['mio_ip_prefix'] + str(userdict['mio_ip_suffix']),
        netmask=userdict['netmask'],
        gateway=userdict['gateway'],
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def check_network_menush(retry_cnt=2, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """Check Network Menush

    As TDE, will check network connection settings to ensure proper connection to network
    """
    userdict = lib.apdicts.userdict

    result = menush.check_network(
        userdict['conn'],
        server=userdict['server'],
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS
# endregion


# region ------------------------------General Tests--------------------------
def get_list_of_two_keys(listofdictindict, keytoiterate, subkey1, subkey2):
    """ Extracts values from 2 keya

    Returns a list of {value1: value2} from a {dict[{dict},{dict},{dictn}]} structure

    :param listofdictindict: {dict[{subkey1:value,subkey2:value},{subkey1:value,subkey2:value},{n}]}
    :param keytoiterate: dict
    :param subkey1: Key to pull value you need
    :param subkey2: Key for other value you need
    :return:list[subkey1,subkey2]
    """

    rtnlist = []
    for item in listofdictindict[keytoiterate]:
        rtnlist.append([item[subkey1], item[subkey2]])

    return rtnlist


def scan_p2c_info():
    """ Scan P2C Info

        As TDE, need a function to scan all information from UUT
        """
    # TODO This part will be changed
    info = lib.get_pre_sequence_info()
    userdict = lib.apdicts.userdict

    userdict['info'] = info
    userdict['container'] = info.super_container
    scan_area(info.areas)

    # -------------------------------MIO Info--------------------------------
    testing_mio = lib.ask_question(question='Vas a probar MIO?',
                                   answers=['Si', 'No'])
    # If process is running MIO, then scan MIO info
    if testing_mio == 'Si':
        log.info('---Scan Blades Under Test Info---')
        uut_pid = lib.ask_question(
            'Escanea el PID de la MIO',
            regex=r'^FPR9K-SUP'
        ).upper()

        uut_sn = lib.ask_question(
            'Escanea el Numero de Serie de la MIO',
            regex=r'^[A-Z0-9]{11}$'
        ).upper()

        userdict['mio_uut'] = uut_pid
        userdict['mio_sn'] = uut_sn

        log.info('Scanned MIO PID: {}'.format(userdict['mio_uut']))
        log.info('Scanned MIO SN: {}'.format(userdict['mio_sn']))

        userdict['mio_test'] = True
    # -----------------------------------------------------------------------

    # -----------------------------Blades Info-------------------------------
    testing_blades = lib.ask_question(question='Vas a probar Blades?',
                                      answers=['Si', 'No'])

    # If process is running Blades, then scan Blades info
    if testing_blades == 'Si':
        log.info('---Scan Blades Under Test Info---')
        container_name = '{}:BLADE '.format(info.containers[0].split(':')[0])

        for slot in xrange(3):
            uut_pid = lib.ask_question(
                'Escanea el PID de la Blade en el slot {}, si no hay unidad ingresa NONE'.format(slot + 1),
                regex=r'^NONE$|^FPR9K-SM-[0-9]{2} V[0-9]{2}$'
            ).upper()

            container = '{}{}'.format(container_name, slot + 1)
            userdict['blades_under_test'][slot]['PID'] = uut_pid
            userdict['blades_under_test'][slot]['Container'] = container

            log.info('Scanned PID: {} in slot: {}'.format(uut_pid, container))

            if uut_pid != 'NONE':
                uut_sn = lib.ask_question(
                    'Escanea el Numero de Serie de la Blade en el slot {}'.format(slot + 1),
                    regex=r'^[A-Z0-9]{11}$'
                ).upper()
                userdict['blade_test'] = True
                userdict['blades_under_test'][slot]['SN'] = uut_sn

        log.info('Blades Under Test: {}'.format(userdict['blades_under_test']))
    # -----------------------------------------------------------------------

    # ------------------------------NetMods Info------------------------------
    testing_netmods = lib.ask_question(question='Vas a probar NetMods?',
                                       answers=['Si', 'No'])

    # If process is running NetMods, then scan NetMods info
    if testing_netmods == 'Si':
        log.info('---Scan NetMods Under Test Info---')
        container_name = '{}:NETMOD '.format(info.containers[0].split(':')[0])

        chassis = lib.ask_question('En que chassis vas a probar?',
                                   answers=['Queens Park', 'Baker'])
        userdict['diag']['prompt'] = 'qpk#' if chassis == 'Queens Park' else 'pad#'
        menush.prompt = userdict['diag']['prompt']

        for slot in xrange(2):
            uut_pid = lib.ask_question(
                'Escanea el PID del NetMod en el slot {}'.format(slot + 1),
                regex=r'^NONE$|^FPR-[D]{0,1}NM-*'
            ).upper()

            container = '{}{}'.format(container_name, slot + 1)
            userdict['netmods_under_test'][slot]['PID'] = uut_pid
            userdict['netmods_under_test'][slot]['Container'] = container

            log.info('Scanned PID: {} in slot: {}'.format(uut_pid, container))

            if uut_pid != 'NONE':
                uut_sn = lib.ask_question(
                    'Escanea el Numero de Serie del NetMod en el slot {}'.format(slot + 1),
                    regex=r'^[A-Z0-9]{11}$'
                ).upper()
                userdict['netmod_test'] = True
                userdict['netmods_under_test'][slot]['SN'] = uut_sn

        log.info('NetMods Under Test: {}'.format(userdict['netmods_under_test']))
    # -----------------------------------------------------------------------

    return lib.PASS


def get_module_info():
    """ Get Module Info

    As TDE, need a function to get and store in userdict the information with which the container was started,
    as PID and SN
    """

    log.info('---Get Module Info---')
    userdict = lib.apdicts.userdict

    userdict['uut_type'] = lib.apdicts.test_info.test_data(field_name='uut_type')
    userdict['vid'] = lib.apdicts.test_info.test_data(field_name='hwrev')
    userdict['sn'] = lib.get_serial_number()
    userdict['area'] = lib.get_test_area()
    userdict['container'] = lib.get_container_name()
    if not ('DEBUG' in userdict['sn'] or 'DEBUG' in userdict['uut_type']):
        get_test_records(
            card='',
            serial=userdict['sn'],
            area='ASSY',
            tan='tan',
            hwrev='tan_ver',
            partnum2='pn',
            hwrev3='hwrev3',
            hwrev2='hwrev2',
            clei='clei',
            eci='eci',
            deviation='deviation',
        )

    if not util.set_uuttype_tmp(userdict['uut_type'], 'uuttype_tmp'):
        return lib.FAIL, userdict['operator_message']

    userdict['cell'] = re.findall('([0-9]+).*([0-9]+)', userdict['container'])[0][0]
    userdict['slot'] = re.findall('([0-9]+).*([0-9]+)', userdict['container'])[0][1]

    log.info('PID: {}'.format(userdict['uut_type']))
    log.info('VID: {}'.format(userdict['vid']))
    log.info('SN: {}'.format(userdict['sn']))
    log.info('Area: {}'.format(userdict['area']))
    log.info('Container: {}'.format(userdict['container']))
    log.info('Cell: {}'.format(userdict['cell']))
    log.info('Slot: {}'.format(userdict['slot']))
    try:
        log.info('TAN: {}'.format(userdict['tan']))
        userdict['tan_ver'] = userdict['hwrev2']
        log.info('TAN Ver: {}'.format(userdict['tan_ver']))
        log.info('PN: {}'.format(userdict['pn']))
        log.info('PN Rev: {}'.format(userdict['hwrev3']))
        log.info('HW Rev 2: {}'.format(userdict['hwrev2']))
        log.info('CLEI: {}'.format(userdict['clei']))
    except KeyError as e:
        log.warning('Cannot get TAN and TAN Ver, SN must be a Dummy or TST Record not found')
        log.warning('Catched Error: {}'.format(str(e)))

    userdict['check_gen'] = True

    try:
        if re.match(r'^BS-DEBUG-MIO$', userdict['uut_type']):
            if userdict['blade_test']:
                userdict['mio_config_blades'] = True
            if userdict['netmod_test']:
                userdict['mio_config_netmods'] = True
            userdict['blade_test'] = False
            userdict['netmod_test'] = False

        elif re.match(r'^FPR9K-SM-[0-9]{2}$', userdict['uut_type']):
            userdict['blade_test'] = True
            userdict['netmod_test'] = False
            userdict['mio_test'] = False

        elif re.match(r'^FPR-[D]{0,1}NM-*|^68-*', userdict['uut_type']):
            userdict['netmod_test'] = True
            userdict['blade_test'] = False
            userdict['mio_test'] = False
            userdict['check_gen'] = userdict[userdict['uuttype_tmp']]['check_gen']
    except Exception, e:
        log.error('Catched Error: {}'.format(str(e)))

    return lib.PASS


def determine_uut():
    '''Determine Units Under Test for Corner Testing Purposes'''
    userdict = lib.apdicts.userdict
    log.debug('RESULT: {}'.format(lib.get_container_name().split()))
    uut_num = lib.get_container_name().split()[2]

    if 'yes' in userdict['UUT {}'.format(uut_num)]['tst_mio']:
        userdict['mio_test'] = True

    if 'yes' in userdict['UUT {}'.format(uut_num)]['tst_blades']:
        if 'BLADE' in lib.get_container_name():
            userdict['blade_test'] = True
        if 'MIO' in lib.get_container_name():
            userdict['mio_config_blades'] = True

    if 'yes' in userdict['UUT {}'.format(uut_num)]['tst_nm']:
        if 'NETMOD' in lib.get_container_name():
            userdict['netmod_test'] = True
        if 'MIO' in lib.get_container_name():
            userdict['mio_config_blades'] = True

    return lib.PASS


def determine_mio_gold():
    """
    Sometimes the MIO used for production does not have ASSY record. To remedy the issue, will skip
    genealogy and area check for these specific MIOs. The specific gold MIO SNs will be structured into
    configuration.py
    :return:
    """
    userdict = lib.apdicts.userdict
    log.info('UUTTYPE = {}'.format(userdict['uut_type']))

    if 'MIO' in userdict['uut_type'] or 'SUP' in userdict['uut_type']:
        log.info('Determining MIO can go thorugh area/genealogy check...')
    if userdict['sn'] in userdict['mio_gold']:
        log.info('*************************************************')
        log.info('GOLD MIO is will skip area/genealogy check.')
        log.info('This MIO can only stay in production as gold unit')
        log.info('Change SN to DEBUG')
        log.info('*************************************************')
        userdict['sn'] = 'DEBUGMIO00{}'.format(lib.get_container_name()[-1:])  # Add the container location as DEBUG SN
    return lib.PASS


def get_test_records(card='', serial='', area='', test_record='P', **parameter_map):
    """
    This function will pull tst records for a given serial Number and
    it will store the information as described bellow:

    If a card values is given it will create a dictionary with records
    found in tst. Dictionary will be stored in user dict as:

        userdict[card]= test_record_dict
        userdict['pinner']={'73_rev': u'B0',
                            '800_rev': u'A0',
                            'uuttype': u'FPR-4120-SUP',
                            '73_pn': u'73-17499-03',
                            '800_pn': u'68-100555-06'}

        card: is the value provided to the function.
        test_record_dict: contain the values availables at TST record.

    If not provided a card value it will create a key in userdict
    dictionary with the value found as the key based in parameter_map.
    Example: found 'partnumber' it will create a key like bellow

        userdict['73_pn']= '73-.....'

    :param card:
    :param serial:
    :param area:
    :param test_record:
    :return:
    """
    userdict = lib.apdicts.userdict

    record_data, record_found = util.pull_test_data(serial, area, test_record)

    if not record_found:
        userdict['operator_message'] = util.operator_message(
            error_message='Test Data cannot be pulled or not available',
            resolution_message='Retry the Test',
        )
        userdict['operator_message'] = "Test Data cannot be pulled or not available."
        return lib.FAIL, userdict['operator_message']

    try:
        log.info('Information of pulled record:')
        log.info('---------------------------------------------')
        log.info('\tSerial Number:{}'.format(serial))

        save_data_to_userdict(card=card, record_data=record_data, **parameter_map)

        log.info('---------------------------------------------')
    except Exception, e:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed {}'.format(util.whoami()),
            resolution_message="Check if all information was added in the {} test area. ".format(area),
        )
        log.error('Catched Error: {}'.format(str(e)))
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def save_data_to_userdict(record_data, card='', **parameter_map):
    """Save Data to Userdict

    Save pulled data from tst records to userdict

    :param record_data:
    :param card:
    :param parameter_map:
    :return:
    """
    userdict = lib.apdicts.userdict
    test_record_dict = {}

    for k, v in parameter_map.items():
        if k in record_data.keys():
            if (card is '') and (v not in userdict or (v in userdict and not userdict[v])):
                userdict[v] = record_data[k]
                log.info('\t {}: {}'.format(v, userdict[v]))
            if card is not '':
                test_record_dict['{}'.format(v)] = record_data[k]
    if card is not '':
        for k, v in test_record_dict.items():
            userdict[card][k] = v
        log.info('\t {} information = {}'.format(card, userdict[card]))


def verify_area(areas_to_check=['ASSY'], skip_fail=False):
    """Verify Area

    As TDE, Need a function to verify previous areas

    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    log.info('---Verify Area---')

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    if lib.get_apollo_mode() == 'DEBUG':
        log.info('Apollo mode is DEBUG, Verify Area wont be performed')
        return lib.PASS
    try:
        for area_to_check in areas_to_check:
            log.info(
                'Verifying Area for:\nSN: {}\nUUT: {}\nAreas: {}'.format(
                    userdict['sn'],
                    userdict['tan'],
                    area_to_check
                ))

            cesiumlib.verify_area(
                serial_number=userdict['sn'],
                uut_type=userdict['tan'],
                area=area_to_check,
                timeframe='30m'
            )

            result = True
    except apexception.ServiceFailure as e:
        log.error('Unit {} does not have previous area {}'.format(userdict['sn'], areas_to_check))
        log.error('Catched Error: {}'.format(str(e)))
        log.error('---Error on Verify Area---')
        result = False
    log.info('---Area Verified---')

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL
    return lib.PASS


def mio_init_status(skip_fail=False):
    """ MIO Init Status

        As TDE, must check if the prev MIO Tests and Init were performed successful,
        if not, then the module (Blade or NetMod) won't continue testing

        :param skip_fail: If True, skip test on Fail
        """

    log.info('-----Getting MIO Init Status-----')

    userdict = lib.apdicts.userdict

    sync_group = re.findall('UUT [0-9]+', userdict['container'])[0]
    mio_container = ''
    for container in lib.get_sync_containers(sync_group):
        if 'MIO' in container:
            mio_container = container
            break
    log.debug('MIO Container Name: {}'.format(mio_container))
    result = lib.get_container_status(mio_container)
    log.info('MIO Container Status: {}'.format(result))

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'FAILED' and not skip_fail:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - MIO Failed on Init'.format(util.whoami()),
            resolution_message='Call support',
        )
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def check_remote_ts():
    '''Check For Remote TS Connection to UUT

    Function to determine if the UUT connection is via a remote Terminal Server
    i.e. NOT telnet 10.1.1.2
    '''
    userdict = lib.apdicts.userdict
    if not menush.check_remote_ts(userdict['conn']):
        return lib.FAIL
    return lib.PASS


def show_connection_info():
    ''' Show UUT Connection Info

    To show within seq logs where the unit is connected for SSH tunneling
    '''
    userdict = lib.apdicts.userdict

    # Show Which AP Server in use
    if lib.get_cached_data('remote_ts') is not None:
        log.debug('Remote Server In Use at: {}'.format(lib.get_cached_data('remote_ts')))
    else:
        log.debug('Server in Use at: {}'.format(lib.get_hostname()))

    # Show UUT IP Address
    log.debug('UUT IP Address: {}{}'.format(userdict['ip_prefix'], userdict['mio_ip_suffix']))
    return


def check_required_files(skip_fail=False):
    """Check Required Files

    As TDE, need a way to insure all pertinent files exist (As programmables, patches, Diag Image, etc)

    :skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    tftpboot_file_keys = userdict['required_files']['tftpboot_files']
    tftpboot_files = []

    for key in tftpboot_file_keys:
        tftpboot_files.append(userdict[key])

    result = util.os_check_files(files=tftpboot_files)

    if 'patches_list' in userdict['required_files'] and result:
        patches_folder = userdict['required_files']['patches_folder']
        patches_list = userdict['required_files']['patches_list']

        for destination in userdict[patches_list]:
            result = util.os_check_files(files=userdict[patches_list][destination], path=userdict[patches_folder])
            if not result and not skip_fail:
                break

    # Print result
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL

    return lib.PASS


# ************************************************************************************
# def verify_area():
#     userdict = lib.apdicts.userdict
#     log.info('--- Verify Area ---')
#
#     pn2check = [userdict['tan']]
#     sn2check = [userdict['sn']]
#
#     if 'genealogy' in userdict:
#         for i in userdict['genealogy']['genealogy_structure']:
#             pn2check.append(i['product_id'])
#             sn2check.append(i['serial_number'])
#
#     return verify_uut_area(sn2check, pn2check)
# ************************************************************************************


# ************************************************************************************
def verify_uut_area(sernum_list, partnum_list):
    userdict = lib.apdicts.userdict
    areas_to_check = 'ASSY'

    if 'MIODUMMY' in sernum_list[0]:
        log.info('Verify area skipped for Dummy SN: {!r}'.format(sernum_list[0]))
        return lib.PASS

    try:
        log.debug('PID: {}'.format(userdict['uut_type']))

        if 'MIO' not in userdict['uut_type']:
            for i in xrange(len(sernum_list)):
                log.info('Verifying Area for:\nSN: {}\nUUT: {}\nAreas: {}'.format(sernum_list[i],
                                                                                  partnum_list[i],
                                                                                  areas_to_check)
                         )

                cesiumlib.verify_area(serial_number=sernum_list[i],
                                      uut_type=partnum_list[i],
                                      area=areas_to_check
                                      )
                log.info('Previous area(s) {!r} ok for SN: {}'.format(areas_to_check, sernum_list[i]))
    except Exception, e:
        log.error('Unit {} does not have previous area {}'.format(userdict['sn'], areas_to_check))
        log.info('Catched Error: {}'.format(str(e)))
        log.info('---Error on Verify Area---')
        return lib.PASS

    log.info('--- Area Verified ---')
    return lib.PASS
# ************************************************************************************


def start_containers():
    """ Start Containers

        As TDE, need a function to start containers that correspond to the information scanned previously at
        scan_p2c_info function, so just the containers that have a UUT will start
        """

    log.info('---Start Containers---')
    userdict = lib.apdicts.userdict

    # Add MIO tst Data
    for container in userdict['info'].containers:
        log.debug('Container: {}'.format(container))
        if 'MIO' in container:
            if userdict['mio_test']:
                lib.add_tst_data(
                    serial_number=userdict['mio_sn'],
                    uut_type=userdict['mio_uut'],
                    test_area=userdict['area'],
                    test_container=container
                )
                log.info('MIO Under Test container Started!')
            else:
                lib.add_tst_data(
                    serial_number='MIODUMMY123',
                    uut_type='FPR9K-SUP',
                    test_area=userdict['area'],
                    test_container=container
                )
                log.info('Dummy MIO container Started!')
            break

    # Start Blades containers (If Necessary)
    for i in xrange(len(userdict['blades_under_test'])):
        blade_uut_type = userdict['blades_under_test'][i]['PID'].split(' ')[0]

        if blade_uut_type == 'NONE':
            continue

        blade_version_id = userdict['blades_under_test'][i]['PID'].split(' ')[1]
        userdict['config_mio'] = True
        blade_sn = userdict['blades_under_test'][i]['SN']
        blade_container = userdict['blades_under_test'][i]['Container']

        log.info('Blade to start:')
        log.info('Serial Number: {}'.format(blade_sn))
        log.info('Container: {}'.format(blade_container))
        log.info('UUT Type: {}'.format(blade_uut_type))
        log.info('VID: {}'.format(blade_version_id))
        log.info('Test Area: {}'.format(userdict['area']))
        log.info('UUT TAN: {}'.format('68-12345-01'))

        lib.add_tst_data(
            serial_number=blade_sn,
            uut_type=blade_uut_type,
            version_id=blade_version_id,
            test_area=userdict['area'],
            test_container=blade_container
        )

        log.info('Blade started!!!')
        log.info('---------------------------------')

    # Start NetMods containers (If Necessary)
    for i in xrange(len(userdict['netmods_under_test'])):
        netmod_uut_type = userdict['netmods_under_test'][i]['PID'].split(' ')[0]

        if netmod_uut_type == 'NONE':
            continue

        netmod_version_id = userdict['netmods_under_test'][i]['PID'].split(' ')[1]
        userdict['config_mio'] = True
        netmod_sn = userdict['netmods_under_test'][i]['SN']
        netmod_container = userdict['netmods_under_test'][i]['Container']

        log.info('NetMod to start:')
        log.info('Serial Number: {}'.format(netmod_sn))
        log.info('Container: {}'.format(netmod_container))
        log.info('UUT Type: {}'.format(netmod_uut_type))
        log.info('Test Area: {}'.format(userdict['area']))
        log.info('UUT TAN: {}'.format('68-12345-01'))

        lib.add_tst_data(serial_number=netmod_sn,
                         uut_type=netmod_uut_type,
                         version_id=netmod_version_id,
                         test_area=userdict['area'],
                         test_container=netmod_container)

        log.info('NetMod started!!!')
        log.info('---------------------------------')

    # if 0:
    #     cesiumlib.get_clei('68-12345-01')

    return lib.PASS


def debug_message_display():
    '''
    22/10/2018: for displaying the standardized debug message through the code
    '''
    userdict = lib.apdicts.userdict
    log.info('*' * 64)
    log.info('The UUT is running in DEBUG mode')
    log.info('This is lab/non-production use only!!!')
    log.info('UUT SN = {}; UUT Type = {}'.format(userdict['sn'], userdict['uut_type']))
    log.info('Current function name = {}'.format(lib.getstepdata()['stepdict']['name']))
    log.info('*' * 64)


def to_boolean(result):
    '''
    Converting the input arg from string to boolean. If the input is already boolean,
    the output will still be boolean (no change)
    '''
    if result == 'Pass':
        result = True
        log.info('result changed from "Pass" to True')
    elif result == 'Fail':
        result = False
        log.info('result changed from "Fail" to False')
    return result


# ************************************************************************************
def add_test_data():
    """ Add Tst Data

        As TDE, Need a function to add tst data in order to go to Sequence from pre Sequence
        """

    log.info('--- Add Test Data ---')
    userdict = lib.apdicts.userdict
    tst_data = {}

    tst_map = {
        'serial_number': 'sn',
        'test_container': 'cell',
        'uut_type': 'tan',
        'test_area': 'area',
        'tan': 'tan',
        'tan_hw_rev': 'hwrev2',
        'diagrev': 'diag_image',
        'version_id': 'tan_ver',
        'clei': 'clei',
        'eci': 'eci',
        'board_part_num': 'pn',
        'board_hw_rev': 'hwrev3'
    }

    if 'DEBUG' in userdict['sn'] or 'DEBUG' in userdict['uut_type']:
        tst_map = {
            'serial_number': 'sn',
            'test_container': 'cell',
            'uut_type': 'uut_type',
            'test_area': 'area',
            'version_id': 'vid',
        }
        log.info('Debug Test Data:')
        log.info('Serial Number: {}'.format(userdict['sn']))
        log.info('Container: {}'.format(userdict['cell']))
        log.info('UUT Type: {}'.format(userdict['uut_type']))
        log.info('UUT VID: {}'.format(userdict['vid']))
        log.info('Test Area: {}'.format(userdict['area']))
    else:
        log.info('Test Data:')
        log.info('Serial Number: {}'.format(userdict['sn']))
        log.info('Container: {}'.format(userdict['container']))
        log.info('UUT Type: {}'.format(userdict['tan']))
        log.info('Test Area: {}'.format(userdict['area']))
        try:
            log.info('UUT TAN: {}'.format(userdict['tan']))
            log.info('UUT TAN ver: {}'.format(userdict['tan_ver']))
            log.info('UUT PN: {}'.format(userdict['pn']))
            log.info('UUT HW Rev 2: {}'.format(userdict['hwrev2']))
            log.info('UUT HW Rev 3: {}'.format(userdict['hwrev3']))
            log.info('CLEI: {}'.format(userdict['clei']))
        except Exception as e:
            log.warning('Some userdict val does not exist')
            log.warning('Error: {}'.format(str(e)))
        log.info('Diagnostic image rev: {}'.format(userdict['diag_image']))
        log.info('Cell #: {}'.format(userdict['cell']))
        log.info('Slot #: {}'.format(userdict['slot']))

    for k, v in tst_map.iteritems():
        if v in userdict.keys() and userdict[v] is not '':
            tst_data[k] = userdict[v]
    tst_data['slot'] = int(userdict['slot'])

    lib.add_tst_data(**tst_data)

    log.info('--- Test Data Added ---')
    return lib.PASS
# ************************************************************************************


# ************************************************************************************
def add_child_tst_data(skip_fail=False):
    """Add Child Test Data to CCC

    :param skip_fail:
    :return:
    """
    log.info("--- Add Module's Daughter Test Data ---")
    userdict = lib.apdicts.userdict
    result = True
    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    if 'genealogy' in userdict:
        parent_sn = userdict['genealogy']['serial_number']
        parent_uuttype = userdict['genealogy']['product_id']

        for i in userdict['genealogy']['genealogy_structure']:
            pn = i['product_id']
            sn = i['serial_number']

            if not pn_in_genealogy(pn):
                log.debug('PN {} Not in Genealogy List'.format(pn))
                continue

            userdict['child_hwrev3'] = ''
            get_test_records(
                card='',
                serial=sn,
                area='ASSY',
                hwrev3='child_hwrev3',
            )

            if userdict['child_hwrev3'] == '':
                log.debug('HWRev3 not found for child SN: {}'.format(sn))
                continue

            log.info('Test Data:')
            log.info('Serial Number: {}'.format(sn))
            log.info('Container: {}'.format(userdict['container']))
            log.info('UUT Type: {}'.format(pn))
            log.info('Test Area: {}'.format(userdict['area']))
            log.info('UUT TAN: {}'.format(userdict['tan']))
            log.info('UUT TAN ver: {}'.format(userdict['tan_ver']))
            log.info('Board PN: {}'.format(pn))
            log.info('Board Ver: {}'.format(userdict['child_hwrev3']))
            log.info('Diagnostic image rev: {}'.format(userdict['diag_image']))
            log.info('Slot #: {}'.format(userdict['slot']))

            lib.add_tst_data(
                serial_number=sn,
                test_container=userdict['container'],
                uut_type=pn,
                test_area=userdict['area'],
                tan=userdict['tan'],
                tan_hw_rev=userdict['tan_ver'],
                board_hw_rev=userdict['child_hwrev3'],
                board_part_num=pn,
                diagrev=userdict['diag_image'],
                slot=int(userdict['slot']),
            )
            result = set_genealogy(parent_sn, parent_uuttype, sn, pn)
        log.info('--- Daughter Test Data Added ---')

    if not result and not skip_fail:
        return lib.FAIL

    return lib.PASS
# ************************************************************************************


# ************************************************************************************
def get_uut_genealogy():
    """ Get NetMod Genealogy
    As TDE, need a function to get NetMod Genealogy
    """
    log.info('--- Get UUT Genealogy ---')
    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    if lib.get_apollo_mode() == 'DEBUG':
        log.info('Apollo mode is DEBUG, genealogy pull wont be performed')
        return lib.PASS

    sernum = userdict['sn']
    partnum = userdict['tan']
    genstructstr = 'genealogy_structure'

    try:
        genealogy = cesiumlib.get_genealogy(sernum, partnum, level=10)
        userdict['genealogy'] = genealogy
        log.info('=======================================')
        for k, v in genealogy.iteritems():
            if k != genstructstr:
                log.info('{}: {}'.format(k, v))
        log.info('** {}'.format(genstructstr))
        for i in genealogy[genstructstr]:
            log.info('***************************************')
            for k, v in i.iteritems():
                log.info('{} : {}'.format(k, v))
        log.info('=======================================')
    except Exception as e:
        log.info('[{}]'.format(e))
        return lib.FAIL

    log.info('--- Genealogy obteined ---')
    return lib.PASS
# ************************************************************************************


# ************************************************************************************
def set_genealogy(parent_sn, parent_uuttype, child_sn, child_pn):
    """Set Genealogy for a given parent and child info

    :param parent_sn:
    :param parent_uuttype:
    :param child_sn:
    :param child_pn:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    log.info('--- Registering genealogy ---')

    try:
        log.info('Parent SN = {} UUT_TYPE = {}, Daughter SN = {} UUT_TYPE = {}'.format(
            parent_sn,
            parent_uuttype,
            child_sn,
            child_pn
        ))
        cesiumlib.assemble_genealogy(parent_sn, parent_uuttype, child_sn, child_pn)
        log.info('--- Genealogy registered ---')
    except Exception as e:
        log.error('Could not register genealogy')
        log.info('Error cached: {!r}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Could not register genealogy'.format(util.whoami()),
            resolution_message='Call support',
        )
        result = False

    return result
# ************************************************************************************


# ************************************************************************************
def pn_in_genealogy(pn):
    """PN In Genealogy

    Determine if Given PN is part of the list of PNs to generate Genealogy

    :param pn: Part No. to check
    :return: True if must generate Genealogy, else False
    """
    userdict = lib.apdicts.userdict
    result = False

    for valid_pn in userdict[userdict['uuttype_tmp']]['genealogy'][userdict['area']]:
        if re.search(valid_pn, pn):
            log.info('PN: {}, matches {}, Genealogy will be set'.format(pn, valid_pn))
            result = True
            break

    return result
# ************************************************************************************


# ************************************************************************************
# def get_tst_data():
#     userdict = lib.apdicts.userdict
#     genstructstr = 'genealogy_structure'
#     userdict['sernums'] = []
#     userdict['partnums'] = []
#     areas = ['ASSY']
#     apollo_debug = 0
#
#     userdict['sernums'].append(userdict['genealogy']['serial_number'])
#     userdict['partnums'].append(userdict['genealogy']['product_id'])
#     for d in userdict['genealogy'][genstructstr]:
#         userdict['sernums'].append(d['serial_number'])
#         userdict['partnums'].append(d['product_id'])
#     try:
#         if lib.get_apollo_mode() == 'DEBUG':
#             apollo_debug = 1
#             log.info('Apollo is in DEBUG mode. Changing to PROD for area validation')
#             lib.set_apollo_mode('PROD')
#
#         for sn in userdict['sernums']:
#             tstdata = cesiumlib.get_legacy_tst(serial_number=sn, areas=areas)
#             userdict['{}_tstdata'.format(sn)] = tstdata
#             log.info('-- Previous tst data info for {!r}:'.format(sn))
#             log.info('{}'.format(tstdata))
#     except Exception as e:
#         log.info('[{}]'.format(e))
#         if apollo_debug:
#             log.info('Changing Apollo to DEBUG again')
#             lib.set_apollo_mode('DEBUG')
#         return lib.FAIL
#
#     if apollo_debug:
#         log.info('Changing Apollo to DEBUG again')
#         lib.set_apollo_mode('DEBUG')
#     return lib.PASS
# ************************************************************************************


def sync_mio(timeout=10000):
    """ Sync MIO

        As TDE, Need a function so the blades and NetMods wait until MIO configuration and tests are performed

        :param timeout
        """

    userdict = lib.apdicts.userdict
    sync_group, module_container = userdict['container'].split(':')

    try:
        lib.sync_group(
            group_name=sync_group,
            timeout=timeout,
            function=wait_for_mio
        )
    except Exception:
        return lib.FAIL

    return lib.PASS


def run_sync_group(group_name='', timeout=10800):
    """ Sync Chamber Members

        Sync Group between all members with the Corner/Chamber Testing Station
        :param timeout - self explanitory
    """
    log.debug("CONTAINER NAME: {}".format(lib.get_container_name().split()))
    try:
        log.info("Sync Group: {}".format(group_name))
        log.info("Members: {}".format(lib.get_sync_containers(group_name=group_name)))
        lib.sync_group(
            group_name=group_name,
            timeout=timeout,
        )
    except Exception:
        return lib.FAIL

    return lib.PASS


def wait_for_mio():
    lib.set_container_text('Waiting for MIO')


def close_connections(power_off_uut=True):
    """ Close Connections

        As TDE, Need a function to close all container connections at the end of a test, and close Power Supplies
        connections just if it is the las container Remaining

        :param power_off_uut Boolean variable to leave UUT Power on Post Test
        """
    userdict = lib.apdicts.userdict
    log.info('Container Status: {}'.format(lib.apdicts.stepdict['current_status']))
    # Display MGMT and BR settings
    if userdict['diag']['prompt'] in userdict['conn'].recbuf:
        menush.display_config(conn=userdict['conn'], module='mgmt')
        menush.display_config(conn=userdict['conn'], module='br')
        util.sende(userdict['conn'], 'exit\r')
    if re.search('gen-apollo@.*$', userdict['conn'].recbuf):
        # Linux Command to display currenlty used MAC address and process
        util.sende(userdict['conn'], 'arp -a\r', expectphrase='gen-apollo@.*$', timeout=100, regex=True)
        util.sende(userdict['conn'], 'ps -a\r', expectphrase='gen-apollo@.*$', timeout=100, regex=True)

    try:
        userdict = lib.apdicts.userdict
        sync_group = ''

        # TODO Modify to work with PCB2C
        for x in re.findall('(UUT [0-9]{1,2})', userdict['container']):
            sync_group = x

        # Determine if Any Containers in Sync Group have status of FAILED
        if lib.get_test_area() == 'PCBP2':
            power_off_uut = determine_pwr(sync_group)

        log.debug('Sync Group: {}'.format(sync_group))
        running_containers = lib.get_running_sync_containers(sync_group)
        log.info('Running Containers: {}'.format(running_containers))
        conns = lib.getconnections()

        # Loop through all connections associated with running container
        for k in conns:
            if 'Chamber' in k:
                continue

            # Skip UUT Power Off if stated
            if not power_off_uut and 'PWR' in k:
                log.debug('DO NOT POWER DOWN UUT')
                show_connection_info()
                continue

            log.debug('Connection: {}'.format(k))  # TODO; raylai; 12/18/2018; if the test area is not 2C, shutting
            if lib.get_test_area() != 'PCB2C':  # the power keep the power on for 2C due to special power constrain
                if ('PWR' in k and len(running_containers) == 1) or ('PWR' not in k):
                    log.info('Powering Off {}'.format(k))
                    conns[k].power_off()
                    log.info('Closing {}'.format(k))
                    conns[k].close()

    except Exception, e:
        log.error('Catched error closing connections, catched Error: {}'.format(str(e)))
        return lib.FAIL

    return lib.PASS


def determine_pwr(sync_group):
    ''' Determine the Power State at End of Testing

    if any containers in a FAILED state, then do not power down
    '''
    for container in lib.get_sync_containers(group_name=sync_group):
        if lib.get_container_status(container) == 'FAILED':
            return False
    return True


def send_failure_note(access_token, room_id):
    '''Send Spark Notification in the event of a failure
    '''
    if lib.get_container_status == 'PASSED':
        return lib.PASS
    failure_note = spark.spark_room(
        access_token=access_token,
        room_id=room_id,
    )
    failure_note.postMsg(message='Unit has failed')
    return lib.FAIL


def cmpd_verify(**kwargs):
    """CMPD Verify
        As TDE, you must define a function to validate cesiumlib.verify_cmpd function with desired values

        :param kwargs: A Dictionary containing necessary CMPD values to verify
            Keys for kwargs must be:
            cmpd_description (string)
            uut_type (string)
            part_number (string)
            part_revision (string)
            test_site (string)
            cmpd_value_list (list)
            password_family (string)
        """

    cmpd_description = kwargs['cmpd_description']
    uut_type = kwargs['uut_type']
    part_number = kwargs['part_number']
    part_revision = kwargs['part_revision']
    test_site = kwargs['test_site']
    cmpd_value_list = kwargs['cmpd_value_list']
    password_family = kwargs['password_family']
    skip_value = kwargs['skip_value']

    result = True
    lib.set_container_text('Verifying CMPD ...')
    userdict = lib.apdicts.userdict
    log.info('---------Verify CMPD-----------')
    try:
        cesiumlib.verify_cmpd(
            cmpd_description=cmpd_description,
            uut_type=uut_type,
            part_number=part_number,
            part_revision=part_revision,
            test_site=test_site,
            cmpd_value_list=cmpd_value_list,
            password_family=password_family,
            skip_value=skip_value
        )
    except Exception, e:
        log.warning('Failed on CMPD Verify')
        log.warning('Catched error: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Failed on CMPD Verify'.format(util.whoami()),
            resolution_message='Call Support',
        )
        result = False

    return result
# endregion


# region ---------------------------MIO Configuration-------------------------
def create_log_directory(skip_fail=False):
    """Create Directory to store Failure Logs

    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict

    result = util.create_repository('/tftpboot/Log_Repository')

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def init_chassis():
    """ VInit Chassis Info

        As TDE, will set and open Chassis connection, and will set the MGMT IP for the Chassis
        """

    userdict = lib.apdicts.userdict

    conns = lib.getconnections()
    userdict['conn'] = conns['CONSOLE']

    userdict['pwr'] = {}
    # Set power connection(s)
    for conn in lib.getconnections():
        if re.match('PWR[1-9]*', conn):
            userdict['pwr'][conn] = lib.getconnections()[conn]

    log.info('Diag image: {}'.format(userdict['diag_image']))
    log.debug('Container Name: {}'.format(userdict['container']))

    chassis_no = ''

    for x in re.findall('UUT ([0-9]+)', userdict['container']):
        chassis_no = x
    log.debug('Chassis No: {}'.format(chassis_no))
    mgmt_ip = (int(chassis_no) * 4) + int(userdict['ip_delta'])
    userdict['mio_ip_suffix'] = mgmt_ip
    log.debug('mgmt IP: {}'.format(userdict['mio_ip_suffix']))

    userdict['mac'] = '{}{}'.format(userdict['mac_prefix'], userdict['mio_ip_suffix'])
    userdict['ip_suffix'] = '{}'.format(userdict['mio_ip_suffix'])

    userdict['br_mac_suffix'] = (hex(int(userdict['mio_ip_suffix']))[-2:]).replace('x', '0')
    userdict['diag_br_mac'] = '{}{}'.format(userdict['diag_mac_preffix'], userdict['br_mac_suffix'])

    log.info('MAC: {}'.format(userdict['mac']))
    log.info('Diag Br MAC: {}'.format(userdict['diag_br_mac']))
    log.info('IP Prefix: {}'.format(userdict['ip_prefix']))
    log.info('IP Suffix: {}'.format(userdict['ip_suffix']))
    log.info('NetMask: {}'.format(userdict['netmask']))
    log.info('Gateway: {}'.format(userdict['gateway']))
    log.info('Server: {}'.format(userdict['server']))

    # Seeting global vat¿riable(diag version) to determine the logic because of diag output changes from 2.1.4
    # if int(re.search('((\d+\.)(\d+\.)(\d+\.)(\d+\.))', userdict['diag_image']).group(0).replace('.', '')) < 2140:
    #     log.info('Diag version is less than 2.1.4.0')
    #     userdict['diag_flag'] = False

    return lib.PASS


def ssh_enter_menu(skip_fail=False):
    """Enter SSH Menu

    SSH connect to an MIO from server (10.1.1.1) using dummy connection

    :param skip_fail: If True, skip test on Fail
    """
    userdict = lib.apdicts.userdict

    result = menush.mio_connect(
        conn=userdict['conn'],
        mio_ip_suffix=userdict['mio_ip_suffix'],
        ip_prefix=userdict['ip_prefix'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {}'.format(util.whoami()),
            resolution_message='Call support',
        )
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def get_blade_imgs(skip_fail=False, skip_fail_pars_list=False, timeout=1000):
    """Get Blade Images

    As TDE, will install blade images in order to test Blades

    :param skip_fail:
    :param skip_fail_pars_list:
    :param timeout:
    :return:
    """
    userdict = lib.apdicts.userdict
    destination_path = '/tmp/.'

    result = menush.get_blade_images(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        img=userdict['blade_image'],
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=timeout
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def init_bridge_to_blades(skip_fail_pars_list=False, skip_fail=False, timeout=100, retry=0):
    """ Init MIO - Blades Bridge

    As TDE, will need to Init a bridge between MIO and Blades to be able to test it
    :param skip_fail
    :param skip_fail_pars_list:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict
    result = False

    try:
        result = menush.set_bridge(
            conn=userdict['conn'],
            timeout=timeout,
            retry=retry,
            skip_fail_pars_list=skip_fail_pars_list,
            ip=userdict['mio_ip_prefix'] + str(userdict['mio_ip_suffix']),
            netmask=userdict['netmask'],
            gateway=userdict['gateway'],
        )

        log.info('Bridge started successfully.')
        if result:
            log.info('Setting Bridge MAC address..')
            result = menush.set_mac(
                userdict['conn'],
                timeout=timeout,
                retry=retry,
                skip_fail_pars_list=skip_fail_pars_list,
                module='br',
                mac=userdict['diag_br_mac'],
            )
            util.sende(userdict['conn'], 'ifconfig -a\r', userdict['diag']['prompt'], timeout=timeout, retry=retry)
    except Exception, e:
        log.error('Catched Error on Init MIO to Blades Bridge: {}'.format(str(e)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Failed to Initialize MIO to Blades Bridge'.format(util.whoami()),
            resolution_message='Call support',
        )
        result = False

    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list=skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS
# endregion


# region ------------------------------MIO Tests------------------------------
def logprintdict(dict, level=0):
    """
    This function will do read human visible a dict, this print the dict with tabs and \n
    using the log info tool
    :param dict: is the dict pobject to be readable
    :param level: is the level start, default is 0, this generate the tab \t accourding to the level
    :return: print log dict readable human
    """

    for key, value in dict.iteritems():
        if type({}) == type(value):
            newlevel = level + 1
            log.info("{}{} :\r".format(('\t' * level), key))
            r = logprintdict(dict[key], newlevel)
            log.info('r = {}'.format(r))
        else:
            log.info("{}{} : {}\r".format(('\t' * level), key, dict[key]))

    return ''


def init_mio(uut_num=None):
    """ Init info for MIO

        As TDE, Init MIO information as its connection and its MGMT IP
        :param uut_num For Corner testing only! Used to indicate which Chassis
    """

    userdict = lib.apdicts.userdict

    lib.set_container_text('Init MIO...')

    try:
        log.info('---Entered MIO Init---')
        # Get connection
        conns = lib.getconnections()

        if uut_num is not None:
            # Corner Testing Setup
            userdict['conn'] = conns['UUT {} CONSOLE'.format(uut_num)]
            userdict['cell'] = uut_num
            userdict['uut_type'] = userdict['UUT {}'.format(uut_num)]['type']
            userdict['area'] = 'PCB2C'
        else:
            userdict['conn'] = conns['CONSOLE']
            log.debug('Connection String: {}'.format(userdict['conn']))
            log.debug('Userdict Container: {}'.format(userdict['container']))

        userdict['pwr'] = {}
        # Set power connection(s)
        for conn in lib.getconnections():
            if re.match('PWR[1-9]*', conn):
                userdict['pwr'][conn] = lib.getconnections()[conn]
            if re.match('UUT {} PWR[1-9]*'.format(uut_num), conn):
                userdict['pwr'][conn] = lib.getconnections()[conn]

        mgmt_ip = (int(userdict['cell']) * 4) + int(userdict['ip_delta'])
        userdict['mio_ip_suffix'] = str(mgmt_ip)
        log.debug('mgmt IP (MIO): {}'.format(userdict['mio_ip_suffix']))

        userdict['mac'] = '{}{}'.format(userdict['mac_prefix'], userdict['mio_ip_suffix'])
        userdict['ip_suffix'] = '{}'.format(userdict['mio_ip_suffix'])

        userdict['br_mac_suffix'] = (hex(int(userdict['mio_ip_suffix']))[-2:]).replace('x', '0')
        userdict['diag_br_mac'] = '{}{}'.format(userdict['diag_mac_preffix'], userdict['br_mac_suffix'])

        log.info('Diag image: {}'.format(userdict['diag_image']))
        log.info('MAC: {}'.format(userdict['mac']))
        log.info('Diag Br MAC: {}'.format(userdict['diag_br_mac']))
        log.info('IP Prefix: {}'.format(userdict['ip_prefix']))
        log.info('IP Suffix: {}'.format(userdict['ip_suffix']))
        log.info('NetMask: {}'.format(userdict['netmask']))
        log.info('Gateway: {}'.format(userdict['gateway']))
        log.info('Server: {}'.format(userdict['server']))

        # Seeting global vat¿riable(diag version) to determine the logic because of diag output changes from 2.1.4
        # if int(re.search('((\d+\.)(\d+\.)(\d+\.)(\d+\.))', userdict['diag_image']).group(0).replace('.', '')) < 2140:
        #     log.info('Diag version is less than 2.1.4.0')
        #     userdict['diag_flag'] = False

    except Exception, e:
        log.error('Catched Error on Init MIO: {}'.format(str(e)))
        return lib.FAIL

    log.info('---MIO Init Successfull---')
    return lib.PASS


def set_settings_rommon(skip_fail=False):
    """Set settings.

    As TDE, will define set_settings_in_rommon so that test set settings.
    :param skip_fail:
    """
    userdict = lib.apdicts.userdict

    # Variables need to be all uppercase
    result = rommon.set_settings(
        userdict['conn'],
        ADDRESS=userdict['ip_prefix'] + userdict['ip_suffix'],
        NETMASK=userdict['netmask'],
        GATEWAY=userdict['gateway'],
        SERVER=userdict['server'],
        TFTP_MACADDR=userdict['mac'],
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def clear_settings_rommon(skip_fail=False):
    """Clear settings.

    As TDE, will define clear_settings_in_rommon so that clear settings.
    :param skip_fail:
    """
    userdict = lib.apdicts.userdict

    # Variables need to be all uppercase
    result = rommon.clear_settings(userdict['conn'])

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


# @test_coverage_console_steps
def check_network_rommon(hardware_check=False, skip_fail_pars_list=False, skip_fail=False):
    """Check Network

    As TDE, will define set_settings_in_rommon so that test set settings.
    :param hardware_check:
    :param skip_fail:
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict

    result = rommon.check_network(
        userdict['conn'],
        userdict['server'],
        timeout=60,
        hardware_check=hardware_check,
        skip_fail_pars_list=skip_fail_pars_list,
        skip_fail=skip_fail
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def boot_rommon(reboot=False, delay_secs=30, skip_fail_pars_list=False, skip_fail=False):
    """Boot rommon.

    As TDE, will define boot_rommon so that test can boot rommon.
    :param skip_fail:
    :param skip_fail_pars_list:
    :param delay_secs:
    :param reboot:If true, the Chassis will be rebooted (With its PS)
    """
    userdict = lib.apdicts.userdict
    result = False

    if reboot:
        log.info('Force reboot')
        result = power_cycle(userdict['pwr'].values(), delay_secs=delay_secs)
    if result:
        # Open Connection to be sure we can write.
        userdict['conn'].open()
        result = rommon.break_autoboot(userdict['conn'], skip_fail_pars_list=skip_fail_pars_list)

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def show_info_in_rommon(skip_fail_pars_list=False, skip_fail=False):
    """Show info.

    As TDE, will define show_info_in_rommon so that test can show info and
    store it for later use.
    :param skip_fail:
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict
    result = True

    userdict['rommon']['info'] = rommon.show_info(userdict['conn'])
    log.info('Rommon info : {}'.format(userdict['rommon']['info']))

    logprintdict(dict(userdict['rommon']['info']), 0)
    #  Check buffer for any key word failures
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL
    return lib.PASS


def show_nvram_in_rommon(skip_fail_pars_list=False, skip_fail=False):
    """

    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True

    userdict['rommon']['nvram'] = rommon.show_nvram(userdict['conn'])
    log.info('NVRam info : {}'.format(userdict['rommon']['nvram']))

    logprintdict(dict(userdict['rommon']['nvram']), 0)
    #  Check buffer for any key word failures
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL
    return lib.PASS


def check_firmware_version(environment, firmwares=[], skip_fail=False):
    """Check Firmware Version.

    As TDE, will define check_firmware_version so that test Firmware upgrade
    :param skip_fail:
    :param firmwares: (list) A list of Firmwares to Check
    :param environment : (string) environment to check current firmaware versions
    """
    userdict = lib.apdicts.userdict

    for firmware in firmwares:
        result = False
        upgrade_required = False
        try:
            expected_version = userdict[environment]['expected_{}_version'.format(firmware.lower())]
            # TODO: Remove after standardize show inventory o/p 'ver' -> 'Version' in diags/menush
            version = 'Version' if 'rommon' in environment else 'Ver'
            current_version = userdict[environment]['info']['{} {}'.format(firmware, version)]
            result = True

            if expected_version != current_version:
                log.info('{} Version Needs to be update to {}! found {}'.format(
                    firmware, expected_version, current_version))
                upgrade_required = True
            else:
                log.info('{} Version Up-to-date {}!'.format(firmware, current_version))

            # Set Flag to update
            userdict['control_step']['update_{}'.format(firmware.lower())] = upgrade_required
            log.info('{} Update Required = {}'.format(firmware, upgrade_required))

            # Check the iteration of the upgrade fucntion
            if userdict['step_iterations']['update_{}'.format(firmware.lower())] >= 2 and \
                    not skip_fail and \
                    upgrade_required:
                return lib.FAIL, 'Error the {} was not updated'.format(firmware)
        except Exception, e:
            log.error('Exception: {}'.format(e))

            util.test_result_log(
                serial_num=userdict['sn'],
                uut_type=userdict['uut_type'],
                result=result,
                test_name='Check {} Version'.format(firmware),
                test_area=userdict['area'],
                comment='Skipped Fail' if skip_fail and not result else '',
                loop_cnt=userdict['iterations'],
            )
    return lib.PASS


def show_inventory_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """Show info.

    As TDE, will define show_info_in_rommon so that test can show info and
    store it for later use.
    :param skip_fail:
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict
    result = True

    userdict['menush']['info'] = menush.diag_mio_show_inventory(userdict['conn'])
    log.info('menush info : {}'.format(userdict['menush']['info']))
    logprintdict(dict(userdict['menush']['info']), 0)

    #  Check buffer for any key word failures
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = False

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL
    return lib.PASS


def verify_mio_sn(skip_fail=False):
    """ Verify MIO SN
        As TDE, need a function to Verify MIO Scanned SN vs Programmed SN

        :param skip_fail: If True, Skip test on Fail
        """

    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    result = menush.inventory_vs_scanned(
        conn=userdict['conn'],
        find_in_inventory='BACK PLANE  SN',
        scanned_value=userdict['sn']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def fan_test(retry=1, timeout=60, skip_fail_pars_list=False, skip_fail=False, tests=None):
    """fan test

    As TDE, will provide method for fan test on uut.
    :param tests:
    :param skip_fail:
    :param skip_fail_pars_list:
    :param timeout:
    :param retry:
    """
    if tests is None:
        tests = []

    userdict = lib.apdicts.userdict

    log.info('retry: {}'.format(retry))

    result = menush.fan_test(
        conn=userdict['conn'],
        fanlevels=userdict['fan_levels'],
        skip_fail_pars_list=skip_fail_pars_list,
        retry=retry,
        timeout=timeout,
        tests=tests,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    # Determine if we should ignore failure
    skip_fail = grab_ignore_fail_list()

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def grab_ignore_fail_list():
    ''' Grab Ignore Fail List

    Based on Test Area and Configuration File Determine if Test Name
    Should be Skipped
    '''
    userdict = lib.apdicts.userdict

    # Only for AP DEBUG Mode use
    if lib.get_apollo_mode() != 'DEBUG':
        return False

    # Determine Test Name to Query
    test_name = util.whoami(depth=2)

    # Find test_name in configuration setting based on area
    object = lib.get_container_attributes()
    test_station = object._read_data()['container_key'].split("|")[2]
    skip_result = userdict.get('skip_fail', {}).get(test_station, {}).get(test_name, False)

    # Display Skip_fail if present
    if skip_result:
        log.debug("SKIP TEST FOR: {} - {}".format(test_station, test_name))

    return skip_result


def detect_epms(skip_fail=False):
    """Detect EPMs

    This step will verify whether the epms are present

    :param skip_fail: This is a flag to skip the fail and continue testing, True is skip and False no skip
    """
    userdict = lib.apdicts.userdict
    result = True
    userdict['control_step']['reinsert_epms'] = False

    userdict['menush']['info'] = menush.diag_mio_show_inventory(userdict['conn'])
    log.info('menush info : {}'.format(userdict['menush']['info']))

    result = read_epms_info(menush_info=userdict['menush']['info'], expected_epm_pid=userdict['expected_epm_pid'])

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    # check after reinsertion
    if not result and not skip_fail:
        if userdict['step_iterations']['reinsert_epms'] == 0:
            userdict['control_step']['reinsert_epms'] = True
            userdict['step_iterations']['reinsert_epms'] += 1
        else:
            log.error('{} After Reinsertion'.format(userdict['operator_message']))
            return lib.FAIL, userdict['operator_message']

        result = util.ask_question(question='Please Reinsert|replace module(s). Yes/No?')
        if not result:
            return lib.FAIL
    else:
        userdict['control_step']['reinsert_epms'] = False
        userdict['step_iterations']['reinsert_epms'] = 0

    return lib.PASS


def read_epms_info(menush_info, expected_epm_pid):
    """Read EPMs Info

    Extract EPMs info from MIO Inventory

    :param menush_info: Dict with MIO Inventory Info
    :param expected_epm_pid: Expected EPM PID
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True
    epms = {}

    for key, value in menush_info.items():
        epm_info = re.search('(EPM\d)\s(.*)', key)
        if epm_info:
            epm_no, epm_key = epm_info.group(1), epm_info.group(2)
            if epm_no not in epms:
                epms[epm_no] = {}
            epms[epm_no][epm_key] = value

            log.info('EPMs:\r{}'.format(epms))

            # Check for undetectable/invalid gold NM
            if not value or ('PID' in epms[epm_no] and expected_epm_pid not in epms[epm_no]['PID']):
                result = False
                log.warning('Expected NM: {}.'.format(userdict['expected_epm_pid']))
                log.warning('Error: {}: {}'.format(key, value))
                userdict['operator_message'] = util.operator_message(
                    error_message='Error: {} - Unable to detect NM or invalid NM inserted.'.format(util.whoami()),
                    resolution_message='Call support',
                )
    # Check for expected number of epms
    if len(epms) != userdict['expected_epm_no']:
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to detect NM.'.format(util.whoami()),
            resolution_message='Call support',
        )

    return result


def update_rommon_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """Update Rommon

   As TDE,will ensure the rommon version is up-to-date
    :param skip_fail:
    :param skip_fail_pars_list:
   """
    userdict = lib.apdicts.userdict
    destination_path = "/mio/fw/."

    result = menush.update_rommon(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        rommon_img=userdict['rommon_image'],
        rommon_prompt=userdict['rommon']['prompt'],
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=300)

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )
    userdict['step_iterations']['update_rommon'] += 1
    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_disk_presence(devices, hardware_check=False, retry=0, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """MIO Device Prescence

    This function is used to detect disk(s) and usb presence at MIO

    :param devices:
    :param hardware_check:
    :param retry:
    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict

    result = menush.mio_disk_presence(
        conn=userdict['conn'],
        devices=devices,
        hardware_check=hardware_check,
        retry=retry,
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def read_temperature(retry=0, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """read temperature

    As TDE, will provide method for read_temperature on uut.
    :param skip_fail:
    :param skip_fail_pars_list:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict

    # Following command is to Activate a mode that allows test Temperature
    util.sende(userdict['conn'], 'sdk -x\r', userdict['diag']['prompt'], 10)

    result = menush.read_temperatures(
        userdict['conn'],
        skip_fail_pars_list=skip_fail_pars_list,
        retry=retry,
        timeout=timeout,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def power_redundancy(retry=0, timeout=120, skip_fail=False):
    """power redundancy

    As TDE, will provide method to test both Power Supplies on a Baker Street Chassis.
    :param skip_fail:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict

    result = menush.power_redundancy(
        conn=userdict['conn'],
        pwr=['PWR1', 'PWR2'],
        retry=retry,
        timeout=timeout
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def update_fpga_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """Update FPGA

   As TDE,will verify and ensure the fpga version is up-to-date
    :param skip_fail:(Boolean) This is a flag to skip the fail and continue testing, with
    :param skip_fail_pars_list:(Boolean) This is a flag list to skip fails
    in a list and continue testing
    """
    userdict = lib.apdicts.userdict
    destination_path = "/mio/fw/."

    result = menush.update_fpga(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        fpga_gold_img=userdict['fpga_gold_image'],
        fpga_upgrade_img=userdict['fpga_upgrade_image'],
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=100
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )
    userdict['step_iterations']['update_bridge-fpga'] += 1
    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def update_pseq_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """Update Rommon

   As TDE,will ensure the rommon version is up-to-date
    :param skip_fail:
    :param skip_fail_pars_list:
   """
    userdict = lib.apdicts.userdict
    destination_path = "/mio/fw/."

    result = menush.update_pseq(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        img=[userdict['ps_bridge_file1'], userdict['ps_bridge_file2']],
        mvimg=[userdict['ps_mv_bridge_file1'], userdict['ps_mv_bridge_file2']],
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=300
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )
    userdict['step_iterations']['update_bridge pseq'] += 1
    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def copy_diags_to_bootflash(retry=1, timeout=60, skip_fail=False):
    """copy_diags_to_bootflash

    As TDE, will provide method forT copy the diag image to the bootflash.
    :param skip_fail:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict

    result = menush.copy_diags_to_bootflash(
        userdict['conn'],
        retry=retry,
        timeout=timeout,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def set_time(skip_fail_pars_list=False, skip_fail=False):
    """Set time.

    As TDE, will define set_time_menush so that test can set correct time.
    :param skip_fail_pars_list:
    :param skip_fail:
    """
    userdict = lib.apdicts.userdict

    logmsg = datetime.datetime.now().strftime('current server date %m/%d/%y %H:%M:%S')
    log.info(logmsg)
    result = menush.set_time(
        conn=userdict['conn'],
        idpromcmd=userdict[userdict['uuttype_tmp']]['idpromcmd'],
        dateoffset=userdict[userdict['uuttype_tmp']]['dateoffset'],
        now=datetime.datetime.now(),
        date_program_format='%m/%d/20%y %H:%M:%S',
        skip_fail_pars_list=skip_fail_pars_list
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_get_idprom_values(board):
    """ Get MIO IDPROM Values

    As TDE, Need a function to read Programmed Values from SPROM

    :param board: Board to get SPROM Values From
    """

    lib.set_container_text('Getting IDPROM Values ...')
    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    log.info('---------Getting programmed IDPROM Fields-----------')
    userdict['sprom_programmed_values'], sprom_values_dict = menush.mio_capture_sprom(
        conn=userdict['conn'],
        expectphrase=userdict['menush']['prompt'],
        sprom_command=board
    )

    log.debug('------------Programmed Values list---------')
    for cmpd_val in userdict['sprom_programmed_values']:
        log.info('{}'.format(cmpd_val))

    return lib.PASS


def mio_verify_sprom(board, skip_fail=False):
    """ CMPD Verify MIO

        As TDE, Need a function to read Verify Programmed Values Vs CMPD Values of a desired Board

        :param board: Board to verify CMPD Values
        :param skip_fail: Skip Fail when True
        """

    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    # -----Add PID and VID and SN to board dict-----
    userdict[board]['pid'] = userdict['uut_type']
    userdict[board]['vid'] = userdict['vid']
    sn = menush.show_mio_idprom_field(conn=userdict['conn'], board=board, field='sn')
    userdict[board]['sernum'] = sn
    get_test_records(
        card=board,
        serial=sn,
        area='ASSY',
        partnum2='pn',
        hwrev3='pnrev',
        tan='tan',
        hwrev='tanrev',
        clei='clei'
    )
    cmpd_dict = userdict[board]
    log.info('-----Verify CMPD Values-----\r{}'.format(cmpd_dict))

    result = cmpd_verify(
        cmpd_description=cmpd_dict['description'],
        uut_type=cmpd_dict['uut_temp'],
        part_number=cmpd_dict['pn'],
        part_revision=cmpd_dict['pnrev'],
        test_site='ALL',
        cmpd_value_list=userdict['sprom_programmed_values'],
        password_family=cmpd_dict['password_family'],
        skip_value=cmpd_dict['skip_value']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_verify_sprom_to_tst(board, skip_fail=False):
    """Verify SPROM to Tst

    This function will compare Test Records of a board (TAN, TAN REV and SN) with the SPROM

    :param board:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    for val in userdict[board]['check_tst']:
        prog_val = menush.read_mio_idprom_field(
            conn=userdict['conn'],
            board=board,
            offset=userdict[userdict['uuttype_tmp']]['{}offset'.format(val)],
            length=userdict[userdict['uuttype_tmp']]['{}length'.format(val)]
        )
        test_val = userdict[board][val]
        log.debug('Test Record {}: {}'.format(val, test_val))
        log.debug('Programmed {}: {}'.format(val, prog_val))

        if test_val == prog_val:
            log.info('{} Matches'.format(val))
        else:
            log.error('{} Does not match'.format(val))
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - Test Record does not Match with programmed Value'.format(util.whoami()),
                resolution_message='Call Support',
            )
            result = False
            break

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_fetch_mac(skip_fail=False):
    """MIO Verify and Program MAC.

    As TDE, will define mio_verify_program_mac so that test can verify if MIO MAC is Legit and if not,
    then program it.

    :param skip_fail: This is a flag to skip the Fail and continue testing
    """
    userdict = lib.apdicts.userdict
    result = True

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    # Read the MAC from the sprom
    try:
        prod_name = userdict['uuttype_tmp']
        idprom_cmd = userdict[prod_name]['idpromcmd']

        offset = userdict[prod_name]['macoffset']
        length = userdict[prod_name]['macoffsetlength']
        userdict['macblocksize'] = userdict[prod_name]['macblocksize']
        userdict[idprom_cmd]['sn'] = userdict['sn']
        userdict[idprom_cmd]['uut_type'] = userdict['uut_type']

        prompt = menush.prompt
        cmd = 'diag mio utils idprom read -d {} -t hex -o {} -r{}'.format(idprom_cmd, offset[0], length)
        util.sende(
            userdict['conn'],
            cmd + '\r',
            expectphrase=prompt,
            timeout=30
        )

        userdict['mac'] = util.get_mac_from_buffer(buffer=userdict['conn'].recbuf)
        log.info('Programmed MAC: {}, MAC Block size: {}'.format(userdict['mac'], userdict[prod_name]['macblocksize']))
        # Upload Programmed MAC Address and BlockSize to CCC
        util.upload_measurement(
            limit_name='Original {} MAC Captured'.format(idprom_cmd),
            capture_value='{}'.format(userdict['mac'])
        )
        util.upload_measurement(
            limit_name='Original {} MAC BlockSize'.format(idprom_cmd),
            capture_value='{}'.format(userdict[prod_name]['macblocksize'])
        )

    except Exception as error_message:
        log.info(error_message)
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Fetch MAC'.format(util.whoami()),
            resolution_message='',
        )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def verify_mac(board='', skip_fail=False):
    """Verify MAC

    As TDE, will define verify_mac so that test can verify if MAC is Legit and if not, then program it.

    :param board:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    userdict['control_step']['program_mac'] = False

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    if board == '':
        prod_name = userdict['uuttype_tmp']
        board = userdict[prod_name]['idpromcmd']

    result, userdict[board]['mac'], block_size = menush.verify_mac(
        sn=userdict[board]['sn'],
        uut_type=userdict[board]['uut_type'],
        block_size=userdict['macblocksize'],
        mac=userdict['mac']
    )

    log.info('-------VERIFY MAC------')
    log.info('Result: {}'.format(result))
    log.info('MAC: {}'.format(userdict[board]['mac']))
    log.info('MAC Block Size: {}'.format(block_size))

    # Set Flag to program mac in case captured MAC is not same as fetch_mac
    if re.sub('[^a-zA-Z0-9]', '', userdict['mac'].lower()) != \
       re.sub('[^a-zA-Z0-9]', '', userdict[board]['mac'].lower()):
        log.info('Need to Program MAC Address {}'.format(userdict[board]['mac']))
        userdict['control_step']['program_mac'] = True

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def mio_program_mac(skip_fail=False, skip_fail_pars_list=False):
    """MIO Program MAC

    Program Necessary MAC Address at MIO

    :param skip_fail:
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    prod_name = userdict['uuttype_tmp']
    board = userdict[prod_name]['idpromcmd']
    offset = userdict[prod_name]['macoffset']
    formatted_mac = userdict[board]['mac']
    result = True

    for sprom_address in offset:
        command = "diag mio utils idprom write -d {} -o {} -w {}".format(
            board,
            sprom_address,
            formatted_mac.replace(':', '').lower()
        )
        prog_mac_result = menush.run_functional_test(
            conn=userdict['conn'],
            test_name='Programm MAC Address',
            test_command=command,
            skip_fail_pars_list=skip_fail_pars_list
        )
        # Upload MAC Programmed to Measurememt list.
        util.upload_measurement(
            limit_name='Programmed {} MAC Captured'.format(board),
            capture_value='{}'.format(userdict[board]['mac'])
        )

        # Print result
        util.test_result_log(
            serial_num=userdict['sn'],
            uut_type=userdict['uut_type'],
            result='Pass' if prog_mac_result else 'Fail',
            test_name='Program MAC at {}'.format(sprom_address),
            test_area=userdict['area'],
            comment='Skipped Fail' if skip_fail and not prog_mac_result else '',
        )

        if not prog_mac_result and not skip_fail:
            log.error('Error found: {}'.format(userdict['operator_message']))
            result = False
            break

        log.info('MAC Programmed')

    if not menush.run_functional_test(
            conn=userdict['conn'],
            test_name='{} Checksun'.format(board),
            test_command='diag mio utils idprom checksum -d {}'.format(board),
            skip_fail_pars_list=skip_fail_pars_list,
    ):
        result = False

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def program_rtc(skip_fail=False):
    """
    This function will program the RTC clock time
    :param skip_fail: This is a flag to skip the Fail and continue testing
    """
    userdict = lib.apdicts.userdict

    date = util.capture_server_time(utc=True)
    log.info('Programming the next date time {}'.format(date))
    result = menush.program_rtc(conn=userdict['conn'], rtc=date)

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def update_fpga_basin_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """Update FPGA Basin

   As TDE,will verify and ensure the fpga basin version is up-to-date
    :param skip_fail:(Boolean) This is a flag to skip the fail and continue testing, with
    :param skip_fail_pars_list:(Boolean) This is a flag list to skip fails
    in a list and continue testing
   """
    userdict = lib.apdicts.userdict
    destination_path = "/mio/fw/."

    result = menush.update_fpga_basin(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        img=userdict['fpga_basin_image'],
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=300
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    userdict['step_iterations']['update_basin fpga'] += 1
    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def update_pseq_basin_in_menush(skip_fail_pars_list=False, skip_fail=False):
    """update PSEQ - Chesham

    As TDE,will ensure the rommon version is up-to-date
    :param skip_fail: This is a flag to skip the failure
    :param skip_fail_pars_list: This is a list flag to skip failures in result lists
    :param image_number: This is the pseq basin number image to re use this step
    :return True or False
    """
    userdict = lib.apdicts.userdict
    result = False
    destination_path = "/mio/fw/."
    img = [userdict['ps_basin_file2'], userdict['ps_basin_file1']]
    mvimg = [userdict['ps_mv_basin_file2'], userdict['ps_mv_basin_file1']]
    result = menush.update_pseq_basin(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        destination_path=destination_path,
        img=img,
        mvimg=mvimg,
        skip_fail_pars_list=skip_fail_pars_list,
        timeout=300
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    userdict['step_iterations']['update_basin m3'] += 1
    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    log.info('Wait for 150 seconds before booting.')
    time.sleep(150)

    return lib.PASS


def set_act2_cmd(module):
    """Set ACT2 Cmd

    Set ACT2 command for MIO or NetMod

    :param module:
    :return:
    """
    userdict = lib.apdicts.userdict
    act2cmd = userdict[userdict['uuttype_tmp']]['act2cmd']

    if module:
        act2cmd = userdict[userdict['uuttype_tmp']]['act2cmd'].format(userdict['module_no'])

    return act2cmd


def mio_verify_act2(certs=['rsa', 'harsa'], fail_if_not_installed=False, module=False, skip_fail=False):
    """MIO ACT2 Necessary

       As TDE,will ensure ACT2 must be Installed on UUT
        :param certs: A list of certs to verify and Install
        :param fail_if_not_installed: Return lib.FAIL if ACT2 is not installed
        :param module: if function is for a module (UCS, NetMod) or for MIO
        :param skip_fail: This is a flag to skip the failure
        :return Apollo PASS or FAIL
       """
    userdict = lib.apdicts.userdict
    userdict['program_act2'] = False

    act2cmd = set_act2_cmd(module)

    for cert in certs:
        result = menush.verify_act2(conn=userdict['conn'], module=act2cmd, cert=cert)

        util.test_result_log(
            serial_num=userdict['sn'],
            uut_type=userdict['uut_type'],
            result='ACT2 {} Already Installed'.format(cert) if result else 'ACT2 Must be Installed',
            test_name=lib.getstepdata()['stepdict']['name'] + ' {}'.format(cert),
            test_area=userdict['area'],
            comment='Skipped Fail' if skip_fail and not result else '',
            loop_cnt=userdict['iterations'],
        )

        if not result and not skip_fail:
            if fail_if_not_installed:
                log.warning('ACT2 {} Verification Failed'.format(cert))
                userdict['operator_message'] = util.operator_message(
                    error_message='Error {} - Failed ACT2 {} Verification'.format(util.whoami(), cert),
                    resolution_message='Call support',
                )
                return lib.FAIL, userdict['operator_message']
            elif userdict['program_act2']:
                log.warning('ACT2 {} Verification Failed after Installation'.format(cert))
                userdict['operator_message'] = util.operator_message(
                    error_message='Error {} - Failed ACT2 {} Installation'.format(util.whoami(), cert),
                    resolution_message='Call support',
                )
                return lib.FAIL, userdict['operator_message']

            userdict['program_act2'] = True
            break

    return lib.PASS


def capture_system_info(retry=1, timeout=60, skip_fail_pars_list=False, skip_fail=False):
    """capture system info

    As TDE, will provide method to test capture system info from uut.
    :param skip_fail:
    :param skip_fail_pars_list:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict

    result = menush.capture_system_info(
        conn=userdict['conn'],
        skip_fail_pars_list=skip_fail_pars_list,
        retry=retry,
        timeout=timeout,
        pid=userdict['uuttype_tmp']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def memory_test(test_name, hardware_check=False, retry=0, timeout=900, skip_fail=False, skip_fail_pars_list=False):
    """memory test

    As TDE, will provide method for memory test on uut.

    :param test_name:
    :param hardware_check:
    :param retry:
    :param timeout:
    :param skip_fail:
    :param skip_fail_pars_list:
    :return:
    """

    userdict = lib.apdicts.userdict

    pid = userdict['uuttype_tmp']
    memory_size = userdict[pid]['memory_size']
    test_command = userdict['functional_test'][test_name] + '{}\r'.format(memory_size)

    result = menush.run_functional_test(
        conn=userdict['conn'],
        test_name=lib.getstepdata()['stepdict']['name'],
        test_command=test_command,
        hardware_check=hardware_check,
        retry=retry,
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list
    )

    # Print result
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def obfl_erase(retry=1, timeout=300, skip_fail_pars_list=False, skip_fail=False):
    """obfl Erase

    As TDE, will provide a method to erase the obfl on uut.
    :param skip_fail:
    :param skip_fail_pars_list:
    :param timeout:
    :param retry:
    """
    userdict = lib.apdicts.userdict

    result = menush.obfl_erase(
        userdict['conn'],
        skip_fail_pars_list=skip_fail_pars_list,
        retry=retry,
        timeout=timeout,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def verify_rtc(skip_fail_pars_list=False, skip_fail=False):
    """verify_rtc

    As TDE, will define verify_rtc so that test can verify correct time.
    :param skip_fail:
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict
    userdict['operator_message'] = ''

    result = menush.verify_rtc(
        userdict['conn'],
        time_delta=45,
        skip_fail=skip_fail,
        skip_fail_pars_list=skip_fail_pars_list,
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mio_activate_fans(timeout=300, skip_fail=False):
    """Activate_fans

        As TDE, will define mio_activate_fans so that FST area can recognize Fans.
        :param timeout:
        :param skip_fail:
        """

    userdict = lib.apdicts.userdict

    result = menush.mio_activate_fans(
        userdict['conn'],
        fan_qty=userdict['fan_levels']['fan_number'] / 2,
        timeout=timeout
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS
# endregion


# region -----------------------------Blades Tests----------------------------
def init_blades():
    """ Init info for Blades

        As TDE, Init Blade information as its connection and its MGMT IP
        """

    lib.set_container_text('Init Blade...')

    try:
        userdict = lib.apdicts.userdict

        station = userdict['area']
        log.info('Area: {}'.format(station))
        log.info('---Entered Blade Init---')
        # Get connection
        conns = lib.getconnections()

        userdict['conn'] = conns['SSH']
        log.debug('Connection String: {}'.format(userdict['conn']))

        userdict['pwr'] = {}
        # Set power connection(s)
        for conn in lib.getconnections():
            if re.match('PWR[1-9]*', conn):
                userdict['pwr'][conn] = lib.getconnections()[conn]

        userdict['module_no'] = userdict['slot']
        log.debug('Blade Number: {}'.format(userdict['module_no']))

        mgmt_ip = (int(userdict['cell']) * 4) + int(userdict['ip_delta'])
        userdict['mio_ip_suffix'] = str(mgmt_ip)
        log.debug('mgmt IP (MIO): {}'.format(mgmt_ip))

        userdict['blade_ip_suffix'] = int(mgmt_ip) + int(userdict['module_no'])
        log.debug('Blade IP: {}'.format(userdict['blade_ip_suffix']))
    except Exception, e:
        log.error('Catched error on Init Blade: {}'.format(str(e)))
        return lib.FAIL

    log.info('---Blade Init Successful---')
    return lib.PASS


def open_connection():
    """ Open Container Connection

        As TDE, will open a container Dummy Connection
        """

    lib.set_container_text('Opening Dummy Connection...')

    try:
        userdict = lib.apdicts.userdict
        conn = userdict['conn']
        log.debug('Dummy Connection: {}'.format(conn))
        log.info('---Open Dummy Connection---')

        conn.power_on()
        log.info('Dummy Connection Openned')
        util.sleep(10)
        util.sende(conn, '\r', 'gen-apollo@.*$', 10, regex=True, retry=5)

    except Exception, e:
        log.error('Catched error openning Dummy Connection: {}'.format(str(e)))
        return lib.FAIL

    log.info('---Dummy Connection Openned Successfully---')
    return lib.PASS


def install_blade_patches(skip_fail=False):
    """ Install Blades Patches

        As TDE, have to install necessary patches for Blades Tests
        """
    userdict = lib.apdicts.userdict

    result = menush.install_patches(
        conn=userdict['conn'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        source_server=userdict['server'],
        patches_path=userdict['patches_path'],
        patches=userdict['patches']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def cd_test_dir():
    """Setup test directory and switch to it for testing"""
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    log.info('-' * 50)
    log.info('Switch directory to /tmp/test for all the testing...')
    util.send(conn, 'mkdir /tmp/test\r', '#', timeout=60)
    util.send(conn, 'cd /tmp/test\r', '#', timeout=60)
    log.info('-' * 50)
    return lib.PASS


def get_time(date_format='%m-%d-%y', seperator='-', hex=False, skip_fail=False):
    """Get time.

    As TDE, will define get_time to get current time and store to program in idprom.

    :param date_format:
    :param seperator:
    :param hex:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = True

    # Set the current time
    userdict['datetime'] = menush.get_time(date_format, seperator, hex)

    if not userdict['datetime']:
        log.warning('Unable to get current time.')
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Fetch Current Time'.format(util.whoami()),
            resolution_message='',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def verify_blade_sn(skip_fail=False):
    """ Veridy Blade SN

        As TDE, will need to Verify Blade Scanned SN vs Programmed SN

        :param skip_fail: If True, skip test on Fail
        """

    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    result = menush.verify_blade_sn(
        conn=userdict['conn'],
        blade_no=userdict['module_no'],
        scanned_sn=userdict['sn']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def fetch_cmpd_sprom():
    """ Fetch CMPD Values for Blades

        As TDE, need to fetch CMPD Values in order to program it to Blade SPROM
        """

    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    eco_dev = userdict[userdict['uuttype_tmp']][userdict['tan']][userdict['tan_ver']]['eco_dev']

    log.debug('>>>>>>>>>>CMPD Info<<<<<<<<<')
    log.debug('CMPD Desription: {}'.format('SPROM'))
    log.debug('UUT Type: {}'.format(userdict['uut_type']))
    log.debug('Part No: {}'.format(userdict['tan']))
    log.debug('Part Rev: {}'.format(userdict['tan_ver']))
    log.debug('Site: {}'.format('ALL'))
    log.debug('Eco: {}'.format(eco_dev))
    log.debug('Password Family: {}'.format(userdict[userdict['uuttype_tmp']]['password_family']))

    log.info('------------Getting values from CMPD-----------')
    userdict['cmpd_types'], userdict['cmpd_values'] = cesiumlib.get_cmpd(
        cmpd_description='SPROM',
        uut_type=userdict['uut_type'],
        part_number=userdict['tan'],
        part_revision=userdict['tan_ver'],
        test_site='ALL',
        eco_deviation_number=eco_dev,
        password_family=userdict[userdict['uuttype_tmp']]['password_family']
    )

    log.debug('******************Got Types:****************')
    for field_type in userdict['cmpd_types']:
        log.info('{}'.format(field_type))
    log.debug('****************Got Values:****************')
    for val in userdict['cmpd_values']:
        log.info('{}'.format(val))

    return lib.PASS


def fetch_cmpd_mp3():
    """Fetch CMPD Values for Moore Park / Moore Park 3 boards
        need to check the MP3 revision. If it is -03 and lower, will fail the CMPD check
    :param board:
    :param idprom_cmd:
    :param skip_fail:
    :param timeout:
    :return:
    """

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    userdict = lib.apdicts.userdict
    boards = {'mezz': 'mezz', 'mlom': 'mlom'}
    if userdict[userdict['uuttype_tmp']]['board_type'] == 'm4':
        # North Wembley boards; use Moor Park version 1
        prefix = 'mp-'
    elif userdict[userdict['uuttype_tmp']]['board_type'] == 'm5':
        # Olympia/Knightsbridge boards; use Moor Park version 3
        prefix = 'mp3-'

    for board in boards:
        log.info('Board = {}'.format(boards[board]))
        # Constructing the MP uuttype_tmp key
        eco_dev = userdict[(prefix + board).upper()]['eco_dev']
        pn_ver = userdict[(prefix + board).upper()]['pn_ver']
        pn_rev = userdict[(prefix + board).upper()]['pn_rev']
        uut_type = userdict[(prefix + board).upper()]['uut_type']

        log.debug('>>>>>>>>>>CMPD Info<<<<<<<<<')
        log.debug('CMPD Desription: {}'.format('SPROM'))
        log.debug('UUT Type: {}'.format(uut_type))
        log.debug('Part No: {}'.format(pn_ver))
        log.debug('Part Rev: {}'.format(pn_rev))
        log.debug('Site: {}'.format('ALL'))
        log.debug('Eco: {}'.format(eco_dev))
        log.debug('Password Family: {}'.format(userdict[userdict['uuttype_tmp']]['password_family']))

        log.info('------------Getting values from CMPD-----------')
        userdict['cmpd_types_{}'.format(board)], userdict['cmpd_values_{}'.format(board)] = cesiumlib.get_cmpd(
            cmpd_description='SPROM',
            uut_type=uut_type,
            part_number=pn_ver,
            part_revision=pn_rev,
            test_site='ALL',
            eco_deviation_number=eco_dev,
            password_family=userdict[userdict['uuttype_tmp']]['password_family']
        )
        log.debug('******************Got Types:****************')
        for field_type in userdict['cmpd_types_{}'.format(board)]:
            log.info('{}'.format(field_type))
        log.debug('****************Got Values:****************')
        for val in userdict['cmpd_values_{}'.format(board)]:
            log.info('{}'.format(val))
        log.info('-' * 60)
    return lib.PASS


def verify_mp3_sprom():
    """Compare the MP3 value from the userdict to the captured value from MP3 EEPROM (MLOM and MEZZ)
        :param board:
        :param idprom_cmd:
        :param skip_fail:
        :param timeout:
        :return:
    """
    userdict = lib.apdicts.userdict
    boards = {'mezz': 'mezz', 'mlom': 'mlom'}
    if userdict[userdict['uuttype_tmp']]['board_type'] == 'm4':
        # North Wembley boards; use Moor Park version 1
        prefix = 'mp-'
    elif userdict[userdict['uuttype_tmp']]['board_type'] == 'm5':
        # Olympia/Knightsbridge boards; use Moor Park version 3
        prefix = 'mp3-'

    for board in boards:
        log.info('Board = {}'.format(boards[board]))
        # Constructing the MP uuttype_tmp key
        board_uuttype_tmp = (prefix + board).upper()
        log.info('board_uuttype_tmp = {}'.format(board_uuttype_tmp))
        # eco_dev = userdict[board_uuttype_tmp]['eco_dev']
        pn_ver = userdict[board_uuttype_tmp]['pn_ver']
        pn_rev = userdict[board_uuttype_tmp]['pn_rev']
        # uut_type = userdict[(prefix + board).upper()]['uut_type']

        userdict[board] = {}
        try:
            # Fetch Idprom values
            util.send(
                userdict['conn'],
                'diag blade{} show {}idprom\r'.format(userdict['module_no'], idprom_cmd),
                expectphrase=userdict['diag']['prompt'],
                timeout=timeout
            )
            # Convert recbuf to dictionary
            mboard = lib.string_to_dict(userdict['conn'].recbuf, ':')

            log.debug('{} Fields:\n{}'.format(board, mboard))

            log.info('Programmed PID: "{}"'.format(mboard['PRODUCT NAME']))
            log.info('Programmed SN : "{}"'.format(mboard['SERIAL NUM']))
            log.info('Programmed Part Num: "{}"'.format(mboard['PART NUM']))
            log.info('Programmed Part Num Rev : "{}"'.format(mboard['PART NUM REV']))

            log.info('-' * 45)
            log.info('Compare product version...')
            if pn_ver == mboard['PART NUM']:
                log.info('Part number version check: OK')
                result = True
            else:
                log.info('Part number version check: NOT OK')
                result = False
            log.info('-' * 45)
            log.info('Compare product revision...')
            if pn_rev == mboard['PART NUM REV']:
                log.info('Part number revision check: OK')
                result = True
            else:
                log.info('Part number revision check: NOT OK')
                result = False
            log.info('-' * 45)

        except Exception as error_message:
            log.info(error_message)
            result = False
            userdict['operator_message'] = util.operator_message(
                error_message='Error: {} - Cannot Fetch {} MAC'.format(util.whoami(), board),
                resolution_message='',
            )
            userdict['failed_sequences'][util.whoami()] = error_message

        util.test_result_log(
            serial_num=mboard['SERIAL NUM'],
            uut_type=userdict[board_uuttype_tmp]['uut_type'],
            result=result,
            test_name=lib.getstepdata()['stepdict']['name'],
            test_area=userdict['area'],
            comment='Skipped Fail' if skip_fail and not result else '',
            loop_cnt=userdict['iterations'],
        )

        if not result and not skip_fail:
            return lib.FAIL, userdict['operator_message']

    return lib.PASS


def program_bmc():
    """ Program Blade BMC

        As TDE, need a function to program fetched values from CMPD to Blade SPROM
        """

    lib.set_container_text('Programming BMC Fields...')

    try:
        userdict = lib.apdicts.userdict
        log.info('---Program BMC Fields---')

        if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
            debug_message_display()
            return lib.PASS

        conn = userdict['conn']
        blade_no = userdict['module_no']

        cmpd_dictionary = dict(zip(userdict['cmpd_types'], userdict['cmpd_values']))
        cmpd_dictionary['SERIAL NUM'] = userdict['sn']
        cmpd_dictionary['MFG DATE'] = userdict['datetime']
        cmpd_dictionary['NUMBER OF MAC'] = '"' + cmpd_dictionary['NUMBER OF MAC'] + '"'  # from 4 to "00 04"
        cmpd_dictionary['CARD TYPE'] = '"' + cmpd_dictionary['CARD TYPE'] + '"'

        log.info('*********CMPD Dictionary*******')
        for x in userdict['cmpd_fields']:
            log.debug("userdict['cmpd_fields'] = {}".format(x))

        # Added for Olympia/Knightsbridge
        # fru_file_id = cmpd_dictionary['FRU FILE ID']
        # prod_part_rev = cmpd_dictionary['PROD PART NUM REV']
        if (userdict['uuttype_tmp'] == 'BS-BD-40-C' or
                userdict['uuttype_tmp'] == 'BS-BD-48-C' or
                userdict['uuttype_tmp'] == 'BS-BD-56-C'):
            # Need to update the program field for OP/KB (M5) blades
            for x in userdict['cmpd_fields']:
                # Update Product Partnum (68-level) (overwrite 'skip' to actual value)
                if x[0] == 'PRODUCT PARTNUM':
                    x[1] = 'prod_part_num'

                # Update the FRU FILE ID (overwrite 'skip' to actual value)
                if x[0] == 'FRU FILE ID':
                    x[1] = 'prod_fru_id'

                # Update Product Part Number (overwrite 'skip' to actual value)
                if x[0] == 'PROD PART NUM REV':
                    x[1] = 'prod_part_rev'

            log.info('-' * 50)
            log.info('Correcting cmpd_fields for M5 (Olympia/Knightsbridge) blades...')
            for x in userdict['cmpd_fields']:
                log.debug("userdict['cmpd_fields'] = {}".format(x))

        log.info('*********CMPD Dictionary*******')
        for cmpd_type in cmpd_dictionary:
            log.info('{}:{}'.format(cmpd_type, cmpd_dictionary[cmpd_type]))

        log.info('------------Values from CMPD fetched-----------')

        log.info('Programming Fetched Values from CMPD...')
        prog_fields = [x for x in userdict['cmpd_fields'] if x[1] != 'skip']
        log.debug('Fields to Program:\n{}'.format(prog_fields))

        menush.enter_menu(conn, userdict['menush']['prompt'])
        for field in prog_fields:
            if field[2] not in cmpd_dictionary:
                log.warning('{} not at CMPD Values, so it wont be programmed'.format(field[2]))
                continue

            test_name = 'Program {}'.format(field[0])
            log.debug('Test Name: {}'.format(test_name))

            cmd = 'blade{}  program bmcfields {} {}\r'.format(
                blade_no,
                field[1],
                '"' + cmpd_dictionary[field[2]] + '"' if 'mfg_info' in field[1] else cmpd_dictionary[field[2]]
            )
            log.debug('Command: {}'.format(cmd))

            result = menush.run_functional_test(
                conn=conn,
                test_name=test_name,
                test_command=cmd,
                expectphrase=userdict['menush']['prompt']
            )

            # Print result
            util.test_result_log(
                serial_num=userdict['sn'],
                uut_type=userdict['uut_type'],
                result=result,
                test_name=test_name,
                test_area=userdict['area'],
                comment='',
            )

            if not result:
                log.error('Error found: {}'.format(userdict['operator_message']))
                return lib.FAIL

        menush.exit_menu(conn, userdict['diag']['prompt'])

        # Adding board_part_no, board_hw_rev and clei
        log.info('>>>>>>>Adding info to Test Data<<<<<<')
        log.info('Part Num: {}'.format(cmpd_dictionary['PART NUM']))
        log.info('TAN HW Rev: {}'.format(userdict['tan_ver']))
        log.info('CLEI: {}'.format(cmpd_dictionary['CLEI']))

        lib.add_tst_data(
            serial_number=userdict['sn'],
            test_container=userdict['container'],
            uut_type=userdict['tan'],
            test_area=userdict['area'],
            board_part_num=cmpd_dictionary['PART NUM'],
            tan_hw_rev=userdict['tan_ver'],
            clei=cmpd_dictionary['CLEI']
        )

    except Exception, e:
        log.error('Catched error on IDPROM Fields Programming: {}'.format(str(e)))
        return lib.FAIL

    log.info('---BMC Fields Programmed---')

    return lib.PASS


def get_blade_idprom_values():
    """ Get Blade IDPROM Values

        As TDE, need a function that reads the SPROM values of a Blade
        """

    lib.set_container_text('Getting IDPROM Values ...')
    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    conn = userdict['conn']
    blade_no = userdict['module_no']

    util.sende(conn, 'diag blade{} show bldidprom\r'.format(blade_no), userdict['diag']['prompt'], 60)

    log.info('---------Getting programmed BMC Fields-----------')
    programmed_fields = lib.string_to_dict(conn.recbuf, ':')
    userdict['sprom_programmed_values'] = []

    log.debug('----------Programmed Values Dic-------- ')
    for cmpd_field in userdict['cmpd_fields']:
        # TODO; adding language code programming bypass. CMPD LANGUAGE CODE field should be "SKIP SPROM CHECK"
        if 'LANGUAGE' in cmpd_field[0]:
            programmed_fields[cmpd_field[0]] = '0'
        log.info('{}:{}'.format(cmpd_field[0], programmed_fields[cmpd_field[0]]))
        userdict['sprom_programmed_values'].append(programmed_fields[cmpd_field[0]])

    log.debug('------------Programmed Values list---------')
    for cmpd_val in userdict['sprom_programmed_values']:
        log.info('{}'.format(cmpd_val))

    return lib.PASS


def cmpd_verify_blade(skip_fail=False):
    """ CMPD Verify for Blade

        As TDE, need a function to verify CMPD Values vs Programmed values in a Blade
        """

    userdict = lib.apdicts.userdict

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    result = cmpd_verify(
        cmpd_description='SPROM',
        uut_type=userdict['uut_type'],
        part_number=userdict['tan'],
        part_revision=userdict['tan_ver'],
        test_site='ALL',
        cmpd_value_list=userdict['sprom_programmed_values'],
        password_family=userdict[userdict['uuttype_tmp']]['password_family'],
        skip_value=userdict[userdict['uuttype_tmp']]['skip_value']
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def blade_fetch_mac(board='', idprom_cmd='', skip_fail=False, timeout=600):
    """Blade Fetch MAC

    This function will read programmed MAC Address at the given board for Blades

    :param board:
    :param idprom_cmd:
    :param skip_fail:
    :param timeout:
    :return:
    """

    userdict = lib.apdicts.userdict
    result = True

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    if board not in userdict:
        userdict[board] = {}

    try:
        # Set MAC variables
        userdict['macblocksize'] = userdict['mac_block_size'][board]
        # Fetch Idprom values
        util.send(
            userdict['conn'],
            'diag blade{} show {}idprom\r'.format(userdict['module_no'], idprom_cmd),
            expectphrase=userdict['diag']['prompt'],
            timeout=timeout
        )
        # Convert recbuf to dictionary
        board_fields = lib.string_to_dict(userdict['conn'].recbuf, ':')

        log.debug('{} Fields:\n{}'.format(board, board_fields))

        log.info('Programmed PID: "{}"'.format(board_fields['PRODUCT NAME']))
        log.info('Programmed Part Num: "{}"'.format(board_fields['PART NUM']))
        log.info('Programmed SN : "{}"'.format(board_fields['SERIAL NUM']))
        log.info('Programmed MAC: "{}"'.format(board_fields['MAC']))
        userdict['board_fields'] = board_fields

        userdict[board]['sn'] = board_fields['SERIAL NUM']
        userdict[board]['uut_type'] = board_fields['PRODUCT NAME']
        userdict['mac'] = board_fields['MAC']
        log.info('Programmed {} MAC: {}, MAC Block size: {}'.format(board, userdict['mac'], userdict['macblocksize']))
    except Exception as error_message:
        log.info(error_message)
        result = False
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot Fetch {} MAC'.format(util.whoami(), board),
            resolution_message='',
        )
        userdict['failed_sequences'][util.whoami()] = error_message

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def blade_program_mac(board='', timeout=200, skip_fail=False, skip_fail_pars_list=False):
    """Program Blade MAC info

    As TDE, will define routine to program the blade MAC values

    :param board:
    :param timeout:
    :param skip_fail:
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict
    mac_key = 'MAC ADDRESS'
    sprom_dict = {}

    if 'DEBUG' in userdict['uut_type'] or 'DEBUG' in userdict['sn']:
        debug_message_display()
        return lib.PASS

    try:
        sprom_dict['{}'.format(mac_key)] = util.convert_mac_address(userdict[board]['mac'], 2, '-')

        result = menush.blade_program_sprom(
            userdict['conn'],
            sprom_keys=[['MAC ADDRESS', 'mac_addr', 'MAC']],
            sprom_values=sprom_dict,
            board_no=userdict['module_no'],
            board=board,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list
        )
    except Exception, error_message:
        log.error('Exception: {}'.format(str(error_message)))
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unable to Program {} MAC Address'.format(util.whoami(), board),
            resolution_message='',
        )
        userdict['failed_sequences'][util.whoami()] = error_message
        result = False
    finally:
        userdict[mac_key] = ''

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def set_date(timeout=30, skip_fail=False):
    """Set Date

    As TDE, need a function to set date to a Blade

    :param timeout:
    :param skip_fail:
    :return:
    """
    lib.set_container_text('Upgrading Date...')
    userdict = lib.apdicts.userdict
    log.info('---PIDs Upgrade---')

    conn = userdict['conn']
    blade_no = userdict['module_no']

    util.sende(conn, 'date -u +\%Y-\%m-\%d\ \%H:\%M:\%S\r', expectphrase=userdict['diag']['prompt'], timeout=timeout)
    date = ''
    for x in re.findall(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}',
            conn.recbuf,
            re.MULTILINE
    ):
        date = x

    log.info('Date to be Set: {}'.format(date))
    test_name = 'set date'
    cmd = userdict['functional_test']['set date'].format(blade_no, date)

    menush.enter_menu(conn, userdict['menush']['prompt'])
    result = menush.run_functional_test(
        conn=conn,
        test_name='set date',
        test_command=cmd,
        expectphrase=userdict['menush']['prompt'],
    )
    menush.exit_menu(conn, userdict['diag']['prompt'])

    # Print result
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=test_name,
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        log.error('Error found: {}'.format(userdict['operator_message']))
        return lib.FAIL

    return lib.PASS


def blade_verify_ssd_info(skip_fail=False, skip_fail_pars_list=False):
    """Blade Verify RAID

    To make sure that Blade SSD info is correct and also to verify that RAID Array was set correctly

    :param must_be_raid: Set it to True to verify that the RAID Array was set correctly
    :param skip_fail:
    :param skip_fail_pars_list:
    :return:
    """
    userdict = lib.apdicts.userdict
    cmd = userdict['functional_test']['show ssd'].format(userdict['module_no'])

    if userdict['sn'] in userdict['blade_gold']:
        log.info('-' * 50)
        log.info('This gold unit is using the older SSD. The result of this test will be ignored!')
        skip_fail = True
        log.info('-' * 50)

    result = menush.blade_verify_ssd_info(
        conn=userdict['conn'],
        cmd=cmd,
        raid_info=userdict[userdict['uuttype_tmp']]['raid_info'],
        skip_fail_pars_list=skip_fail_pars_list
    )

    # Print result
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL

    return lib.PASS


def upgrade_bios(upg, hardware_check=False, retry=0, timeout=1800, skip_fail_pars_list=False):
    """Upgrade BIOS

    As TDE, will define a function to be able to upgrade bios on a specified board

    :param upg:
    :param hardware_check:
    :param retry:
    :param timeout:
    :param skip_fail_pars_list:
    :return:
    """

    lib.set_container_text('Upgrading {}...'.format(upg))

    try:
        userdict = lib.apdicts.userdict
        log.info('---{} Upgrade---'.format(upg))

        conn = userdict['conn']
        blade_no = userdict['module_no']

        test_name = upg
        test_command = userdict['functional_test']['bios upgrade'].format(
            blade_no,
            upg,
            userdict[userdict['uuttype_tmp']]['bmc_pid']
        ) + '\r'

        result = menush.run_functional_test(
            conn=conn,
            test_name=test_name,
            test_command=test_command,
            hardware_check=hardware_check,
            retry=retry,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list
        )

        # Print result
        util.test_result_log(
            serial_num=userdict['sn'],
            uut_type=userdict['uut_type'],
            result='Pass' if result else 'Fail',
            test_name=test_name,
            test_area=userdict['area'],
            comment=''
        )

        if not result:
            log.error('Error found: {}'.format(userdict['operator_message']))
            return lib.FAIL

    except Exception, e:
        log.error('Catched error Upgrading {}: {}'.format(upg, str(e)))
        return lib.FAIL

    log.info('---{} Upgraded---'.format(upg))
    return lib.PASS


def verify_blade_act2(fail_if_not_installed=False, skip_fail_pars_list=False):
    """ ACT2 Necessary

    As TDE, need a function to verify if ACT2 is already installed or not in a Blade

    :param fail_if_not_installed: Return lib.FAIL if ACT2 is not installed, else return lib.PASS
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict
    userdict['program_act2'] = False

    need_act2, result = menush.blade_verify_act2(
        conn=userdict['conn'],
        bin_image=userdict['bin_image'],
        module_no=userdict['module_no'],
        ip_prefix=userdict['ip_prefix'],
        blade_ip_suffix=userdict['blade_ip_suffix'],
        netmask=userdict['netmask'],
        gateway=userdict['gateway'],
        server=userdict['server'],
        skip_fail_pars_list=skip_fail_pars_list
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment=''
    )

    if not result:
        return lib.FAIL

    if need_act2:
        if 'DBGPCB' in userdict['area']:  # raylai; 04/14/2019; If installing ACT2 in the DBGPCB test area
            userdict['program_act2'] = True
            return lib.PASS
        if ('PCBP2' in userdict['area'] and fail_if_not_installed) or 'PCBP2' not in userdict['area']:
            return lib.FAIL
        else:
            userdict['program_act2'] = True

    return lib.PASS


def blade_led_test(led_colors=[], timeout=200, skip_fail_pars_list=False, skip_fail=False):
    """Blade LED Test

    This function is to test if LED are in color green or amber (Or depends on the ledcolors param)
    This will send a command (power On/Off x86) to set LED color and ask to the operator if the LED corresponds to
    the color

    :param led_colors: List of LED Colors to test
    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    lockname = 'LED Question'
    result = True

    for color in led_colors:
        test_name = 'Blade LED {}'.format(color)
        test_command = userdict['functional_test']['led {}'.format(color.lower())].format(userdict['module_no'])

        result = menush.run_functional_test(
            conn=userdict['conn'],
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list,
            test_name=test_name,
            test_command=test_command,
        )

        util.test_result_log(
            serial_num=userdict['sn'],
            uut_type=userdict['uut_type'],
            result=result,
            test_name=test_name,
            test_area=userdict['area'],
            comment='Skipped Fail' if skip_fail and not result else '',
        )

        if not result:
            break

        try:
            lock.initialize_lock_state(name=lockname)
            lock_result, result_msg = lock.acquire_lock(name=lockname, wait_timeout=36000, release_timeout=10800)
            if lock_result:
                blade_led = lib.ask_question(
                    question='Blade LED must be {}'.format(color.upper()),
                    answers=['Pass', 'Fail'],
                    media_path='media/LED_{}.jpeg'.format(color.lower())
                )
                if blade_led != 'Pass':
                    userdict['operator_message'] = util.operator_message(
                        error_message='Error: {} - Blade LED {} Failed'.format(util.whoami(), color.upper()),
                        resolution_message='Call support',
                    )
                    result = False
                    break
        except Exception, e:
            log.error('Exception: {}'.format(e))
            result = False
        finally:
            lock.release_lock(name=lockname)
            lock.finalize_lock_state(name=lockname)

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


def blade_led_locator_test(skip_fail=False):
    """Blade LED Locator

    This test is to ask to the operator if the LED Locator is Blinking
    This function will not send any command, the operator have to press the button and then answer if the LED is
    properly blinking

    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict
    lockname = 'LED Question'
    result = True

    try:
        lock.initialize_lock_state(name=lockname)
        lock_result, result_msg = lock.acquire_lock(name=lockname, wait_timeout=36000, release_timeout=10800)
        if lock_result:
            blade_led = lib.ask_question(
                question='Press Blue LED. Blade LED must be BLINKING BLUE',
                answers=['Pass', 'Fail'],
                media_path='media/LED_blue.jpeg'
            )

            if blade_led != 'Pass':
                userdict['operator_message'] = util.operator_message(
                    error_message='Error: {} - Blade LED BLINKING BLUE Failed'.format(util.whoami()),
                    resolution_message='Call support',
                )
                result = False
    except Exception, e:
        log.error('Exception: {}'.format(e))
        result = False
    finally:
        lock.release_lock(name=lockname)
        lock.finalize_lock_state(name=lockname)

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    return lib.PASS


# TODO; raylai; will need to remove the custom power up sequence once the new ACT retry works
def power_cycle_to_diag():
    """
    Adding power cycle and also boot from ROMMON to diag, load diag, add patches, and init bridge
    :return:
    """
    # TODO; raylai; add graeful shutdown here
    try:
        conns = lib.getconnections()
        ps_1 = conns['PWR1']
        ps_2 = conns['PWR2']

        log.info('------------Powering Off Power Supplies------------')
        ps_1.power_off()
        ps_2.power_off()
        log.info('--------------Power Supplies are Off---------------')
        util.sleep(10)
    except Exception, e:
        log.error('Could not turn off unit. Error: {}'.format(str(e)))
        return lib.FAIL
    boot_diag()
    set_mac_menush()
    set_network_menush()
    check_network_menush()
    install_blade_patches()
    get_blade_imgs()
    init_bridge_to_blades()
    return


def blade_program_act2(certs=[], timeout=200, skip_fail_pars_list=False, skip_fail=False):
    """Program Act2

    As TDE, will provide way to program uut with Act2 authentication to qualify authentic cisco products

    :param certs: List of certs to install
    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    """
    userdict = lib.apdicts.userdict

    certs = userdict[userdict['uuttype_tmp']]['certs']
    log.info('Installing the following certs: {}'.format(certs))

    retry_max = 3
    retry = 0
    while retry < retry_max:
        result = menush.blade_program_act2(
            conn=userdict['conn'],
            sn=userdict['sn'],
            cert=certs,
            bin_image=userdict['bin_image'],
            module_no=userdict['module_no'],
            ip_prefix=userdict['ip_prefix'],
            mio_ip_suffix=userdict['mio_ip_suffix'],
            blade_ip_suffix=userdict['blade_ip_suffix'],
            netmask=userdict['netmask'],
            gateway=userdict['gateway'],
            server=userdict['server'],
            credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list,
        )
        if result is True:
            print('ACT2 Programming Passed...')
            retry = retry_max
        else:
            print('ACT2 Programming Failed...')
            retry += 1
            if retry >= retry_max:
                    print('Maximum retry reached...')
                    return 'FAIL'
            print('=' * 60)
            print('Retry programming! Retry #{}'.format(retry))
            print('=' * 60)
        continue

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Program Blade ACT2 Failed'.format(util.whoami()),
            resolution_message='Call support',
        )
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def mcclient(timeout=200, skip_fail_pars_list=False, skip_fail=False):
    """ACT2 Necessary

    As TDE, need a function to perform all MCClient Process before an ACT2 installation was done

    :param timeout:
    :param skip_fail_pars_list:
    :param skip_fail:
    :return:
    """
    userdict = lib.apdicts.userdict

    result = menush.blade_mcclient(
        conn=userdict['conn'],
        sn=userdict['sn'],
        module_no=userdict['module_no'],
        ip_prefix=userdict['ip_prefix'],
        mio_ip_suffix=userdict['mio_ip_suffix'],
        blade_ip_suffix=userdict['blade_ip_suffix'],
        netmask=userdict['netmask'],
        gateway=userdict['gateway'],
        server=userdict['server'],
        bin_image=userdict['bin_image'],
        credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
        timeout=timeout,
        skip_fail_pars_list=skip_fail_pars_list
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL

    return lib.PASS


def functional_test(test_name,
                    module=False,
                    timeout=1800,
                    hardware_check=False,
                    retry=0,
                    skip_fail=False,
                    skip_fail_pars_list=False):
    """Functional Test.
    As TDE, will provide to perform functional test

    :param test_name: Name of the test to be performed
    :param module: (Boolean) if true, puts userdict['module_no'] at the test cmd (example. Blade{} show bldidprom)
    :param timeout
    :param hardware_check
    :param retry: How many times test must retry on Fail
    :param skip_fail: If True, test skips on Fail
    :param skip_fail_pars_list:
    """
    userdict = lib.apdicts.userdict
    conn = userdict['conn']
    result = False
    log_result = True
    tries = 0
    retry_flag, retry_cnt = True if retry > 0 else False, retry
    bios_timeout = False

    test_command = userdict['functional_test'][test_name]
    if module:
        test_command = test_command.format(userdict['module_no'])

    # Check if the gold blade has the proto CPU; will not impact production
    if test_name == 'verify cpu' and userdict['sn'] in userdict['blade_gold']:
        log.info('-' * 50)
        log.info('This gold unit is using the proto CPU. The result of this test will be ignored!')
        skip_fail = True
        log.info('-' * 50)

    # Get MenuSH Result Status
    while not result and tries <= retry:
        # TODO; raylai; Diag will incorporate the power cycle at later release
        if bios_timeout:
            log.info('Power cycle unit.')
            functional_test('pwrcyclex86', True)
        log.info('Test command: {}'.format(test_command))
        if tries > 0:
            log.info('Cmd "{}" Failed. Retrying test...'.format(test_command))

        result = menush.run_functional_test(
            conn=conn,
            test_name=test_name,
            test_command=test_command,
            hardware_check=hardware_check,
            retry=retry,
            timeout=timeout,
            skip_fail_pars_list=skip_fail_pars_list
        )
        tries += 1

        # Save Failed test logs
        if not result:
            if re.search('time[d]*\s*out', conn.recbuf, re.IGNORECASE):
                log.debug('BIOS timeout.')
                log.debug('Retry again....')
                bios_timeout = True
            log_result = menush.save_logs(
                conn=conn,
                expectphrase=userdict['diag']['prompt'],
                test_name=test_name,
                buffer=conn.recbuf,
                credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
                destination_server=userdict['server'],
                destination_path='/tftpboot/Log_Repository'
            )
            if lib.get_cached_data('LOG File_{}'.format(lib.get_container_name())) is not None:
                '''Retry if BIOS timed out; starts here'''
                # log_tar = lib.get_cached_data('LOG File_{}'.format(lib.get_container_name()))
                # util.sende(conn,
                #            'tar -xzOf {} | grep -i "time[d]*\s*out"\r'.format(log_tar),
                #            expectphrase=userdict['diag']['prompt'],
                #            timeout=timeout,
                #            retry=retry)
                # log.debug('Timeout phrases from Log: {}'.format(conn.recbuf))
                # if int(sum(1 for phrase in re.finditer('time[d]*\s*out', conn.recbuf, re.IGNORECASE))) > 0:
                #     log.debug('BIOS timeout.')
                #     log.debug('Retry again....')
                #     # if retry is already set as parameter , then increase by 1 else set to 1
                #     retry += 1 if (retry_flag and retry <= retry_cnt + 1) else 1
                '''Retry if BIOS timed out; ends here'''
                log_result = menush.upload_logs(
                    conn=userdict['conn'],
                    expectphrase='gen-apollo*',
                    test_name=test_name,
                    credentials={'id': userdict['apollo']['id'], 'password': userdict['apollo']['password']},
                    source_path='/tftpboot/Log_Repository',
                    destination_path='/tftpboot/Log_Repository'
                )

    log.debug('Menush Result for cmd "{}", after {} tries: {}'.format(test_command, tries, result))
    # Print result
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=test_name,
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    util.upload_measurement(limit_name='{}'.format(test_name.upper()), capture_value='PASSED' if result else 'FAILED')

    if (not result or not log_result) and not skip_fail:
        log.error('Error found: {}'.format(userdict['operator_message']))
        return lib.FAIL
    return lib.PASS
# endregion


# *************************************************************************************************************
# *************************************************************************************************************

# region ----------------------------NetMods Tests----------------------------
# ************************************************************************************
def show_temp():
    lib.set_container_text('Getting unit Temperature...')

    try:
        userdict = lib.apdicts.userdict
        conn = userdict['conn']
        log.info('---Show Temperatre---')

        menush.enter_menu(conn, userdict['menush']['prompt'])

        util.sende(conn, 'mio show temp\r', userdict['menush']['prompt'], 60)
        log.debug('Temperature:\n{}'.format(conn.recbuf))

    except Exception, e:
        log.error('Catched error on Show Temperature: {}'.format(str(e)))
        return lib.FAIL

    log.info('---Temperature Shown---')
    return lib.PASS
# ************************************************************************************
# endregion

# *************************************************************************************************************
# *************************************************************************************************************


# region ---------------------------2C Functions------------------------------
def ask_question():
    """ Ask Question

        As TDE, Need a function to ask for the UUT at PCB2C
        """

    userdict = lib.apdicts.userdict
    info = lib.get_pre_sequence_info()
    userdict['info'] = info
    area = info.areas[0]        # Notes: First is 'PCB2C' in this case
    pids = info.pids_by_area(area)
    log.debug('List of pids: {}'.format(pids))

    for index, container in enumerate(info.containers):
        answer = lib.ask_question('Test container {}?'.format(container), answers=['YES', 'NO'])
        if answer in ['YES']:
            uut = re.sub(r"Chamber:UUT [1-9] ", '', container).split(' ')[0]
            log.debug('UUT: {}'.format(uut))
            sn = "{}{:02d}".format(uut, index)
            if uut == 'BLADE':
                userdict['blade_test'] = True
                uut = 'FPR9K-SM-44'
            if uut == 'MIO':
                uut = 'FPR9K-SUP'
            lib.add_tst_data(serial_number=sn, test_container=container, uut_type=uut, test_area=area)

    return lib.PASS


def init_2c():
    """
    UUT and chamber initialization
    """
    userdict = lib.apdicts.userdict
    log.debug('Container Name: {}'.format(userdict['container']))
    chamber_init(first_init=False)
    return lib.PASS


def final():
    """
    Do clean up before closing tests
    NOTES: PLEASE DO NOT RUN CHAMBER RAMP AT FINAL STEP !!
    """
    global chamber_handler
    try:
        uut_final()
    finally:
        # Only allow the last UUT container do chamber finalization
        ChamberInterface.stop(chamber_handler)
        lib.apdicts.userdict.clear()
    return lib.PASS


def uut_final():
    """ UUT finalization, do nothing """
    userdict = lib.apdicts.userdict
    if 'MIO' in userdict['uut_type']:
        try:
            conns = lib.getconnections()
            ps_1 = conns['PWR1']
            ps_2 = conns['PWR2']

            log.info('------------Powering Off Power Supplies------------')
            ps_1.power_off()
            ps_2.power_off()
            log.info('--------------Power Supplies are Off---------------')
            util.sleep(10)
        except Exception, e:
            log.error('Could not turn off unit. Error: {}'.format(str(e)))
            return lib.FAIL

    return lib.PASS


def power_cycle_chamber_conn():
    '''Power cycle the chamber connection'''
    conns = lib.getconnections()
    chamber_conn = conns['Chamber']

    log.info('------------Powering Off Chamber Connection ------------')
    chamber_conn.power_off()
    time.sleep(5)
    log.info('------------Powering On  Chamber Connection ------------')
    chamber_conn.power_on()
    log.info('Chamber connection power cycle completed')
    time.sleep(3)
    return lib.PASS


def chamber_final():
    """
    Go to room temperature, and stop chamber
    Only allow the last container do chamber finalization
    """
    global chamber_handler
    if lib.apdicts.stepdict['current_status'] != 'PASS':
        ChamberInterface.stop(chamber_handler)
    return lib.PASS


def chamber_init(first_init=True, fi_action='pause', group_name=None):
    """
    Chamber initialize - create object and set temperature profile
    :return:
    """
    global chamber_handler
    global chamber_profile
    # userdict = lib.apdicts.userdict

    # answer = ''
    # log.info('chamber_handler = {}'.format(str(chamber_handler.chamber)))
    # if 'simulator' in str(chamber_handler):
    #     log.warning('Using chamber simulator!')
    #     while 'Y' not in answer:
    #         answer = lib.ask_question("WARNING: Using chamber simulator. Enter 'Y' to continue.").upper()
    #     for site in userdict['cm_sites']:
    #         if site in lib.get_hostname().upper():
    #             return lib.FAIL, 'Failing because we are using a simulator at CM site {}'.format(site)

    # Initialize chamber handler
    chamber_handler = ChamberInterface.init(
        chamber_profile,
        lib.conn.Chamber,
        first_init=first_init,
        fi_action=fi_action,
        sync_group=group_name,
    )
    # Once chamber start()/ramp()/soak()/test() is failed, invoke stop() automatically
    chamber_handler.autostop_on_error(AMBIENT, DRY, -10)
    return lib.PASS


def chamber_start():
    """
    Chamber start - config chamber and start to run
    :return:
    """
    global chamber_handler
    try:
        ChamberInterface.start(chamber_handler)
    except Exception:
        log.error('*************************************')
        log.error('Chamber issue: ChamberInterface.start')
        log.error('*************************************')
        return lib.FAIL
    return lib.PASS


def chamber_ramp(action=AMBIENT):
    """
    Chamber temperature ramp up/down to the temperature defined in profile
    :param action
    """
    global last_action
    global chamber_handler
    last_action = action
    log.debug("chamber_handler: {}".format(chamber_handler))
    try:
        ChamberInterface.ramp(chamber_handler, action=action)
    except Exception:
        log.error('************************************')
        log.error('Chamber issue: ChamberInterface.ramp')
        log.error('************************************')
        return lib.FAIL
    return lib.PASS


def chamber_start_monitor():
    """
    Start to monitor temperature in chamber during test.
    If set MONITOR_IN_TEST as True, this step will be bypassed.
    :return:
    """
    global chamber_handler
    try:
        ChamberInterface.monitor_start(chamber_handler, MONITOR_IN_TEST)
    except Exception:
        log.error('*********************************************')
        log.error('Chamber issue: ChamberInterface.monitor_start')
        log.error('*********************************************')
        return lib.FAIL
    return lib.PASS


def chamber_stop_monitor():
    """
    Stop to monitor temperature in chamber after test is done.
    If set MONITOR_IN_TEST as True, this step will be bypassed.
    :return:
    """
    try:
        ChamberInterface.monitor_stop(MONITOR_IN_TEST)
    except Exception:
        log.error('********************************************')
        log.error('Chamber issue: ChamberInterface.monitor_stop')
        log.error('********************************************')
        return lib.FAIL
    return lib.PASS


def stop_chamber():
    """Stop Chamber

    """
    global chamber_handler
    try:
        ChamberInterface.stop(chamber_handler, action1="AMBIENT", action2="DRY", target_temp=-10)
    except Exception:
        log.error('********************************************')
        log.error('Chamber issue: ChamberInterface.stop_chamber')
        log.error('********************************************')
        return lib.FAIL
    return lib.PASS


def chamber_profile(obj):
    # Temperature profile - Cold (Need to set the profile by order - ramp, soak, test !!)
    obj.set_profile_ramp(COLD, temperature=5, rate=2, margin=8, max_humidity=0)
    obj.set_profile_soak(COLD, margin=8, duration=1, max_humidity=0)
    obj.set_profile_test(COLD, margin=8, max_humidity=0)
    # Temperature profile - Hot
    obj.set_profile_ramp(HOT, temperature=40, rate=3, margin=5, max_humidity=0)
    obj.set_profile_soak(HOT, margin=5, duration=1, max_humidity=0)
    obj.set_profile_test(HOT, margin=5, max_humidity=0)
    # Temperature profile - Ambient (1st is used for hot to ambient; 2nd is for cold to ambient)
    obj.set_profile_ramp(AMBIENT, temperature=25, rate=3, margin=5, max_humidity=0)
    obj.set_profile_ramp(DRY, temperature=35, rate=3, margin=3, max_humidity=0)
# endregion


######################
# Pre-test sequences #
######################
def load_configuration():
    """Load configuration.

    As TDE, will define load_configuration so that configuration can be define
    in one place.
    """
    userdict = lib.apdicts.userdict

    # Import configuration data
    for k, v in configuration.data.iteritems():
        userdict[k] = v
    for k, v in userdict.iteritems():
        log.info('{}: {}'.format(k, v))

    # ----------- Tests by Pedro Rgz-------------
    # # To Get TAN from get_tan with PID and CLEI
    # tans = cesiumlib.get_tan('FPR-NM-4X40G', 'FWUIAAPAAA')
    # log.info('{}'.format(tans))
    # lib.ask_question('EPM TANs: {}'.format(tans), regex='Y')
    #
    # tans = cesiumlib.get_tan('FPR9K-SUP', 'FWUCAAFBAF')
    # log.info('{}'.format(tans))
    # lib.ask_question('MIO TANs: {}'.format(tans), regex='Y')

    # # To Get TAN and Rev from print_label with SN
    # debug = False
    # if 'DEBUG' in lib.get_apollo_mode():
    #     debug = True
    #     lib.set_apollo_mode('PROD')
    #
    # label_format = '<tan>,<hwrev>'
    # label_tags = dict(serial_number='FLM2151061L', areas='ASSY',)
    # tan_rev = cesiumlib.print_label(
    #     destination_directory='/tmp/',
    #     label_format=label_format,
    #     generate_file=False,
    #     **label_tags)
    #
    # if debug:
    #     lib.set_apollo_mode('DEBUG')
    #
    # log.debug('Print Label Result: {}'.format(tan_rev))
    # a = lib.ask_question('Print Label Result: {}. Continuar? [Y|N]'.format(tan_rev), regex='Y|N')
    # if 'N' in a:
    #     return lib.FAIL
    # ------------------------------

    return lib.PASS


def scan_sysft_info():
    """Scan UUT info.

    As TDE, will define scan_sysft_info so that operator can scan UUT
    information.
    """
    info = lib.get_pre_sequence_info()
    userdict = lib.apdicts.userdict

    log.info('Pre-sequence information given by VStation')
    for area in info.areas:
        log.info('Area/PIDs:  {}/{}'.format(area, info.pids_by_area(area)))
    log.info('Containers:      {}'.format(info.containers))
    log.info('username:        {}'.format(info.username))
    log.info('gui_type:        {}'.format(info.gui_type))

    for i, container in enumerate(info.containers):
        ip_suffix = i + 10
        if ' ' in container:
            ip_suffix = int(container.split(' ')[1]) + 10
        userdict['ip_suffix'] = str(ip_suffix)

        log.info('Continer:        {}'.format(container))
        scan_area(info.areas)
        scan_sn()
        scan_pidvid(info.pids_by_area(userdict['area']))
        scan_pnrev('68')
        scan_lineid()

        sernum = userdict['sn']
        uuttype = userdict['pid']
        parent = 'SELF'
        result = 'START'
        test = 'Record Start'

        userdict['uut tracking'] = [
            ['* SERNUM *',
             '* UUTTYPE *',
             '* PARENT *',
             '* RESULT *',
             '* TEST *']
        ]
        map_parent_child_tmp = [sernum, uuttype, parent, result, test]
        userdict['uut tracking'].append(map_parent_child_tmp)

        # will display each UUT in a nice organized/lined-up columns
        util.display_parent_child_mtx(userdict['uut tracking'])
        log.info('Recording {} as sn in {} mode'.format(userdict['sn'], lib.get_apollo_mode()))

        if 'PROD' == lib.get_apollo_mode():
            backflush_status = 'YES'
        else:
            backflush_status = 'NO'

        lib.add_tst_data(
            test_container=container,
            serial_number=userdict['sn'],
            uut_type=userdict['pid'],
            lineid=int(userdict['lineid']),
            version_id=userdict['vid'],
            test_area=userdict['area'],
            backflush_status=backflush_status
        )

    return lib.PASS


def scan_area(valid_areas):
    """Scan area.

    As TDE, will define scan_area so that operator can scan test area.
    :param valid_areas
    """
    userdict = lib.apdicts.userdict

    if 'area' not in userdict.keys():
        userdict['area'] = ''

    # Scan area
    while True:
        if not userdict['area']:
            if len(valid_areas) > 1:
                userdict['area'] = lib.ask_question('Enter area {}'.format(valid_areas)).upper()
            else:
                userdict['area'] = valid_areas[0]
        if userdict['area'] not in valid_areas:
            log.warning('Invalid area {} entered!  Valid areas are {}.'.format(userdict['area'], valid_areas))
            userdict['area'] = ''
            continue
        break
    log.info('Area:            {}'.format(userdict['area']))


def scan_sn():
    """Scan serial number.

    As TDE, will define scan_sn so that operator can scan serial number.
    """
    userdict = lib.apdicts.userdict

    if 'sn' not in userdict.keys():
        userdict['sn'] = ''

    # Scan serial number
    while True:
        if not userdict['sn']:
            userdict['sn'] = lib.ask_question('Enter serial number').upper()
        if 'DEBUG' in userdict['sn']:
            break
        if not re.match(r'^(JMX|TSP)[A-Z0-9]{8}$', userdict['sn']):
            log.warning('Invalid serial number {} entered!'.format(userdict['sn']))
            userdict['sn'] = ''
            continue
        break
    log.info('Serial Number:   {}'.format(userdict['sn']))


def scan_pidvid(valid_pids):
    """Scan PIDVID.

    As TDE, will define scan_pidvid so that operator can scan PIDVID.
    :param valid_pids
    """
    userdict = lib.apdicts.userdict

    if 'pidvid' not in userdict.keys():
        userdict['pidvid'] = ''

    # Scan PIDVID
    while True:
        if not userdict['pidvid']:
            userdict['pidvid'] = lib.ask_question('Enter PIDVID').upper()
        if 'DEBUG' in userdict['pidvid']:
            userdict['pid'] = 'DEBUG'
            userdict['vid'] = 'DEBUG'
            break
        if not re.match(r'^.* \w{3}$', userdict['pidvid']):
            log.warning('Invalid PIDVID "{}" entered!  Must include a VID.'.format(userdict['pidvid']))
            userdict['pidvid'] = ''
            userdict['pid'] = ''
            userdict['vid'] = ''
            continue
        userdict['pid'], userdict['vid'] = userdict['pidvid'].split(' ')
        break
    log.info('PIDVID:          {} {}'.format(userdict['pid'], userdict['vid']))


def scan_quack_label():
    """Scan Quack Label.

    As TDE, will define scan_quack_label so that operator can scan the quack label
    """
    userdict = lib.apdicts.userdict

    if 'quack_label' not in userdict.keys():
        userdict['quack_label'] = ''

    while True:
        if not userdict['quack_label']:
            userdict['quack_label'] = lib.ask_question('SCAN QUACK LABEL:').upper()
        if 'DEBUG' in userdict['quack_label']:
            userdict['quack_label'] = 'DEBUG'
            break

        if not re.match(r'^[M]{1}[0-9]{8}$', userdict['quack_label']):
            log.warning('Invalid quack label "{}" entered!  Must start with "M" and include 8 digits.'.format(
                userdict['quack_label']
            ))
            userdict['quack_label'] = ''
            continue
        break
    log.info('Quack label:     {}'.format(userdict['quack_label']))


def scan_deviation():
    """Scan deviation.

    As TDE, will define scan_deviation so that operator can scan deviation number
    """
    userdict = lib.apdicts.userdict

    if 'deviation' not in userdict.keys():
        userdict['deviation'] = ''

    # Scan deviation
    while True:
        if not userdict['deviation'] or userdict['deviation'] == '':
            userdict['deviation'] = lib.ask_question('SCAN DEVIATION: [NONE TO SKIP]').upper()
        if 'DEBUG' in userdict['deviation']:
            userdict['deviation'] = 'DEBUG'
            break
        if 'NONE' in userdict['deviation']:
            userdict['deviation'] = 'NONE'
            break
        if not re.match(r'^[D]{1}[0-9]{6}$', userdict['deviation']):
            log.warning('Invalid deviation "{}" entered!  Must start with "D" and include 6 digits.'.format(
                userdict['deviation']
            ))
            userdict['deviation'] = ''
            continue
        break
    log.info('Deviation number: {}'.format(userdict['deviation']))


def scan_pnrev(pn_type='68'):
    """Scan part number and revision.

    As TDE, will define scan_pnrev so that operator can scan part number and
    revision.
    """
    userdict = lib.apdicts.userdict

    if 'pnrev' not in userdict.keys():
        userdict['pnrev'] = ''

    # Set reqular expression based on arguement.  Need to use re.escape to introduce a variable
    pn_regex = r'^' + re.escape(pn_type) + r'-\d*-\d{2} \w\d$'

    log.info('regular expression used: {}'.format(pn_regex))

    # Scan part number rev
    while True:
        if not userdict['pnrev']:
            userdict['pnrev'] = lib.ask_question('Enter part number rev').upper()
        if 'DEBUG' in userdict['pnrev']:
            userdict['pn'] = 'DEBUG'
            userdict['rev'] = 'DEBUG'
            break

        if not re.match(pn_regex, userdict['pnrev']):
            log.warning('Invalid part number rev "{}" entered!  Must start with {}- and include rev.'.format(
                userdict['pnrev'],
                pn_type,
            ))
            userdict['pnrev'] = ''
            continue

        userdict['pn'], userdict['rev'] = userdict['pnrev'].split(' ')
        break
    log.info('Part Number Rev: {} {}'.format(userdict['pn'], userdict['rev']))
    # Check VID against PN
    try:
        if userdict[userdict['pn']]['expected_vid'] != userdict['vid']:
            log.error('   Scanned VID : {}'.format(userdict['vid']))
            log.error('   Expected VID: {}'.format(userdict[userdict['pn']]['expected_vid']))
            log.error('                 MISMATCH!')
            raise Exception('Scanned vs Expected VID Mismatch!')
        else:
            log.info('   Scanned VID : {}'.format(userdict['vid']))
            log.info('   Expected VID: {}'.format(userdict[userdict['pn']]['expected_vid']))
    except KeyError:
        if '68-100282' in userdict['pn'] or 'FPR9K-SM-' in userdict['pid']:
            log.info('   Scanned vs Expected VID check not needed!')
        else:
            raise Exception('No Info found for [{}] in configuration file.'.format(userdict['pn']))


def set_pidvid():
    """Set pidvid based on 73pn.

    As TDE, will define set_pidvid so that script can set pidvid based on a pn
    """
    userdict = lib.apdicts.userdict

    if 'pidvid' not in userdict.keys():
        userdict['pidvid'] = ''

    if userdict['pidvid']:
        userdict['pid'], userdict['vid'] = userdict['pnrev'].split(' ')
    else:
        userdict['pidvid'] = userdict['pnrev']
        userdict['pid'] = userdict['pn']
        userdict['vid'] = userdict['rev']

    log.info('PIDVID:          {} {}'.format(userdict['pid'], userdict['vid']))


def set_pnrev():
    """Set part number and revision.

    As TDE, will define set_pnrev so that script can set pn based on pid vid
    """
    userdict = lib.apdicts.userdict

    if 'pnrev' not in userdict.keys():
        userdict['pnrev'] = ''

    if userdict['pnrev']:
        userdict['pn'], userdict['rev'] = userdict['pnrev'].split(' ')
    else:
        userdict['pnrev'] = userdict['pidvid']
        userdict['pn'] = userdict['pid']
        userdict['rev'] = userdict['vid']

    log.info('Part Number Rev: {} {}'.format(userdict['pn'], userdict['rev']))


def scan_lineid():
    """Scan line ID.

    As TDE, will define scan_lineid so that operator can scan line ID.
    """
    userdict = lib.apdicts.userdict

    if 'lineid' not in userdict.keys():
        userdict['lineid'] = ''

    # Scan lineid
    while True:
        if not userdict['lineid']:
            userdict['lineid'] = lib.ask_question('Enter line ID').upper()
        if 'DEBUG' in userdict['lineid']:
            break
        if not re.match(r'^[0-9]{7}$|^[0-9]{9}$|^[0-9]{10}$', userdict['lineid']):
            log.warning('Invalid line ID "{}" entered!  Must 7, 9  or 10 digits.'.format(userdict['lineid']))
            userdict['lineid'] = ''
            continue
        break
    log.info('Line ID:         {}'.format(userdict['lineid']))


def do_areacheck(areas=[], timeframe='6m', skip_fail=False):
    """Area check.

    As TDE, will define do_areacheck so that test can valid UUT has gone
    through correct process.
    """
    userdict = lib.apdicts.userdict
    result = True

    # Scan area
    # while not areas:
    #    areas = lib.ask_question('Enter previous areas to be checked separated by commas ","').upper()
    # areas = 'PASTE,ICT'
    if ',' in areas:
        areas = areas.split(',')

    log.info('SN:         {}'.format(userdict['sn']))
    log.info('PID:        {}'.format(userdict['pid']))
    log.info('Areas:      {}'.format(areas))
    log.info('Time Frame: {}'.format(timeframe))

    try:
        cesiumlib.verify_area(userdict['sn'], userdict['pid'], areas, timeframe=timeframe)
    except apexceptions.ServiceFailure as error_message:
        result = False
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

    # Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error {} - UUT Failed Area Check'.format(util.whoami()),
            resolution_message='Call support',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['uut_type'],
        result='Pass' if result else 'Fail',
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def get_order(skip_fail=False):
    """Get order.

    As TDE, will define get_order so that test can check the UUT is build
    correctly.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'
    userdict['operator_message'] = ''
    userdict['ordered_hw'] = {}
    userdict['ordered_sw'] = {'fxos': {}, 'csp_apps': []}

    scan_lineid()
    if 'DEBUG' in userdict['lineid']:
        error_message = 'Skip getting order "{}"!'.format(userdict['lineid'])
        log.warning(error_message)
        userdict['failed_sequences'][util.whoami()] = error_message
        return lib.PASS
    try:
        log.info('lineid: {}'.format(userdict['lineid']))
        userdict['lineid_config'] = cesiumlib.get_lineid_config(major_line_id=int(userdict['lineid']))
        userdict['lineid_meta_config'] = cesiumlib.get_lineid_meta_config(userdict['lineid_config'])
        userdict['sw_images'] = cesiumlib.get_lineid_swimages(userdict['lineid_config'])
        userdict['top_level_pid'] = cesiumlib.get_lineid_toplevel_product_id(userdict['lineid_config'])['prod_name']
        if 'config_data' in userdict['lineid_config'].keys():
            userdict['lineid_config_data'] = userdict['lineid_config']['config_data']
        log.info('lineid_config:      {}'.format(userdict['lineid_config']))
        log.info('lineid_meta_config: {}'.format(userdict['lineid_meta_config']))
        log.info('sw_images:          {}'.format(userdict['sw_images']))
        log.info('top_level_pid:      {}'.format(userdict['top_level_pid']))
        log.info('Line ID Config')

        for k, v in userdict['lineid_config'].iteritems():
            if 'config_data' != k:
                log.info('    {}: {}'.format(k, v))
        if 'lineid_config_data' in userdict:
            log.info('    config_data:')
            for item in userdict['lineid_config_data']:
                if item['prod_name'] in userdict['allowed_pid_options']:
                    if not item['prod_name'] in userdict['ordered_hw']:
                        userdict['ordered_hw'][item['prod_name']] = item['qty']
                    else:
                        userdict['ordered_hw'][item['prod_name']] += item['qty']

                log.info('        {}.{}: {} - qty {}'.format(
                    item['level'],
                    item['atlinenum'],
                    item['prod_name'],
                    item['qty'],
                ))

        log.info('SW Config')
        for k, v in userdict['sw_images'].iteritems():
            if 'sw_config' == k:
                for i, item in enumerate(v):
                    log.info('    {} {}:'.format(k, i + 1))
                    for k2, v2 in item.iteritems():
                        log.info('        {}: {}'.format(k2, v2))
                    # Get FXOS Info
                    if 'FXOS' in item['prod_name']:
                        userdict['ordered_sw']['fxos'] = {'image_pid': item['prod_name'],
                                                          'image_name': item['image_name'],
                                                          'image_version': item['image_version']}
                    # Get CSP Application
                    elif 'ASA' in item['prod_name']:
                        userdict['ordered_sw']['csp_apps'].extend([{'image_pid': item['prod_name'],
                                                                    'image_name': item['image_name'],
                                                                    'image_version': item['image_version']}])
            else:
                log.info('    {}: {}'.format(k, v))
    except apexceptions.ServiceFailure as error_message:
        result = 'Fail'
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

    if userdict['ordered_sw']['fxos']['image_name'] not in userdict.keys():
        raise Exception('Info for [{}] not defined '
                        'in configuration file.'.format(userdict['ordered_sw']['fxos']['image_name']))

    # Specify Operator message
    if result is False:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed Get Order',
            resolution_message='Ensure unit has proper LID',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def download_image(skip_fail=False):
    """Download Image.

    As TDE, will define download_image so that required SW is copied to UUT.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'
    userdict['operator_message'] = ''

    fxos_scope('firmware', True)
    userdict['conn'].send(text='show package {} detail\r'.format(userdict['ordered_sw']['fxos']['image_name']),
                          expectphrase='firmware #')
    if 'Version' in userdict['conn'].recbuf:
        log.info('   Bundle Image [{}] already exists.'.format(userdict['ordered_sw']['fxos']['image_name']))
    else:
        userdict['conn'].send(text='download image tftp://{}/{}\r'.format(
            userdict['server_ip'],
            userdict['ordered_sw']['fxos']['image_name']))

        userdict['conn'].send(text='scope download-task {}\r'.format(userdict['ordered_sw']['fxos']['image_name']),
                              expectphrase='download-task #', timeout=10)

        while True:
            userdict['conn'].send(text='show detail\r', expectphrase='download-task #', timeout=10)
            download_state = re.findall('State: ?(.*)\r', userdict['conn'].recbuf)

            if 'Downloaded' in download_state:
                log.info('   - [{}] download completed.'.format(userdict['ordered_sw']['fxos']['image_name']))
                break
            elif 'Downloading' in download_state:
                log.info('   - Downloading ... Waiting 30 secs ...')
                time.sleep(30)
                continue
            elif 'Failed' in download_state:
                result = 'Fail'
                log.info('   - Download Failed!')
                break

    # Get Bundle Image Names
    fxos_scope('firmware', True)
    userdict['conn'].send(text='show bundle {} expand\r'.format(userdict['ordered_sw']['fxos']['image_name']),
                          expectphrase='firmware #', timeout=10)
    userdict['ordered_sw']['fxos']['infra_image'] = re.findall('(\S+infra\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['server_image'] = re.findall('(\S+server\S+)', userdict['conn'].recbuf)[0]

    userdict['conn'].send(text='show bundle {} expand\r'.format(userdict['ordered_sw']['fxos']['infra_image']),
                          expectphrase='firmware #', timeout=10)
    userdict['ordered_sw']['fxos']['kickstart_image'] = re.findall('(\S+kickstart\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['manager_image'] = re.findall('(\S+manager\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['system_image'] = re.findall('(\S+system\S+)', userdict['conn'].recbuf)[0]

    userdict['conn'].send(text='show bundle {} expand\r'.format(userdict['ordered_sw']['fxos']['server_image']),
                          expectphrase='firmware #', timeout=10)
    userdict['ordered_sw']['fxos']['ssp_os_image'] = re.findall('(\S+lfbff\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['adapter_image'] = re.findall('(\S+vic\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['bios_image'] = re.findall('(\S+bios\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['board_controller_image'] = re.findall('(\S+brdprog\S+)',
                                                                          userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['cimc_image'] = re.findall('(\S+cimc\S+)', userdict['conn'].recbuf)[0]
    userdict['ordered_sw']['fxos']['raid_controller_image'] = re.findall('(\S+mrsasctlr\S+)',
                                                                         userdict['conn'].recbuf)[0]

    userdict['conn'].send(text='end\r', expectphrase='-A#')

    log.info('   - Infra Image            : [{}]'.format(userdict['ordered_sw']['fxos']['infra_image']))
    log.info('   - Server Image           : [{}]'.format(userdict['ordered_sw']['fxos']['server_image']))
    log.info('   - Kickstart Image        : [{}]'.format(userdict['ordered_sw']['fxos']['kickstart_image']))
    log.info('   - Manager Image          : [{}]'.format(userdict['ordered_sw']['fxos']['manager_image']))
    log.info('   - System Image           : [{}]'.format(userdict['ordered_sw']['fxos']['system_image']))
    log.info('   - SSP OS Image           : [{}]'.format(userdict['ordered_sw']['fxos']['ssp_os_image']))
    log.info('   - Adapter Image          : [{}]'.format(userdict['ordered_sw']['fxos']['adapter_image']))
    log.info('   - Bios Image             : [{}]'.format(userdict['ordered_sw']['fxos']['bios_image']))
    log.info('   - Board Controller Image : [{}]'.format(userdict['ordered_sw']['fxos']['board_controller_image']))
    log.info('   - CIMC Image             : [{}]'.format(userdict['ordered_sw']['fxos']['cimc_image']))
    log.info('   - Raid Controller Image  : [{}]'.format(userdict['ordered_sw']['fxos']['raid_controller_image']))

    # Specify Operator message
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='Download Failed',
            resolution_message='Contact Test Engineer',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def clean_bootflash(skip_fail=False):
    """Clean bootflash

    This will clean bootflash.
    """

    userdict = lib.apdicts.userdict
    result = 'Pass'
    userdict['operator_message'] = ''

    userdict['conn'].send(text='exit\r', expectphrase='login:', timeout=5)
    userdict['conn'].send(text='adminbackup\r', expectphrase='Password:')
    userdict['conn'].send(text='\r', expectphrase='Linux#')

    userdict['conn'].send(text='rm -rf /bootflash/mfg\r', expectphrase='Linux#')
    userdict['conn'].send(text='ls /bootflash/mfg\r', expectphrase='Linux#')

    if 'No such file or directory' not in userdict['conn'].recbuf:
        result = 'Fail'

    userdict['conn'].send(text='exit\r', expectphrase='login:')
    userdict['conn'].send(text='admin\r', expectphrase='Password:')
    userdict['conn'].send(text='{}\r'.format(userdict['os']['admin_password']), expectphrase='-A#')

    # Specify Operator message
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='Clean Bootflash Failed',
            resolution_message='Contact Test Engineer',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def fxos_install_image(skip_fail=False):

    userdict = lib.apdicts.userdict
    result = 'Pass'
    userdict['operator_message'] = ''

    fxos_scope('chassis 1', True)
    userdict['conn'].send(text='show version detail\r', expectphrase='chassis #')

    expected_package_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_package_version']
    fxos_install_bundle_image(expected_package_version, 3600, True)

    fxos_scope('chassis 1', True)
    userdict['conn'].send(text='show version detail\r', expectphrase='chassis #')

    # Specify Operator message
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='FXOS Install Failed',
            resolution_message='Contact Test Engineer',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def download_software(skip_fail=False):
    """Download Software.

    As TDE, will define download_software so that required SW is available in local host.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'
    userdict['operator_message'] = ''

    scan_lineid()
    if 'DEBUG' in userdict['lineid']:
        error_message = 'Skip downloading software "{}"!'.format(userdict['lineid'])
        log.warning(error_message)
        userdict['failed_sequences'][util.whoami()] = error_message
        return lib.PASS
    try:
        cesiumlib.sync_software_by_lineid(major_line_id=int(userdict['lineid']),
                                          wait_for_result=True,
                                          timeout_minutes=30)
    except apexceptions.ServiceFailure as error_message:
        result = 'Fail'
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

    # Specify Operator message
    if result is False:
        userdict['operator_message'] = util.operator_message(
            error_message='Failed Download Software',
            resolution_message='Ensure sync_software_by_lineid service is working',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


###################
# Sequences Steps #
###################
def init():
    """Init.

    As TDE, will define init so that test can initialize variables.
    """

    userdict = lib.apdicts.userdict
    userdict['iterations'] = 0

    info = lib.get_my_container_key()
    index = int(info.split('|')[3][-2:])

    ip_suffix = int(userdict['mio_ip_suffix'])
    userdict['mio_ip_suffix'] = str(ip_suffix + index)
    userdict['mio_ip'] = userdict['mio_ip_prefix'] + userdict['mio_ip_suffix']

    userdict['conn'] = lib.conn.CONSOLE1

    return lib.PASS


def finish(skip_close=False):
    """Finish.

    As TDE, will define finish so that test can do the necessary cleanup.
    """
    userdict = lib.apdicts.userdict

    if 'conn' in userdict.keys() and not skip_close:
        userdict['conn'].power_off()

    result = 'Pass'
    userdict['tar_path'] = "/tftpboot/"

    if userdict['failed_sequences']:
        result = 'Fail'
        log.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        log.warning('Below are failed sequences, but skipped recording failure:')
        log.warning('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        for k, v in userdict['failed_sequences'].iteritems():
            log.warning('{}: {}'.format(k, v))

    util.test_summary_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        area_loop_cnt=userdict['iterations'],
        user_name=lib.apdicts.test_info.user_name,
        result=result,
        test_area=userdict['area'],
    )

    log.warning('Creating now TAR file.....')
    tarmsg = datetime.datetime.now().strftime('%m/%d/%y %H;%M;%S')
    tarmsg2 = datetime.datetime.now().strftime('%m/%d/%y %H;%M;%S')
    log.info(tarmsg)
    log.info(tarmsg2)

    tarfile = userdict['tar_path'] + userdict['sn'] + '.TAR'
    userdict['tar_list'] = 'S' + userdict['sn'] + '\n' + 'CCISCO' + '\n' + 'p5' + '\n' + 'BNONE' + '\n' + \
                           'NAjmxavp15' + '\n' + 'P' + userdict['area'] + '\n' + 'S' + 'UUT1' + \
                           '\n' + 'OAutoprog' + '\n' + 'L2' + '\n' + 'rA' + '\n' + 'T' + 'PASS' + '\n' + '[' + \
                           tarmsg + '\n' + ']' + tarmsg2
    with open(tarfile, 'w') as f:
        f.write(''.join(userdict['tar_list']))

    lib.apdicts.userdict.clear()

    log.info("Current date & time " + time.strftime("%c"))

    if lib.get_apollo_mode == 'Prod' and result == 'Fail':
        return lib.FAIL
    return lib.PASS


def select_func():
    """Select Function to Run Next

    To be used as a debug method to allow the operator or developer to run only
    what they need when they need it. Goes well with PyTest
    """
    functions = inspect.getmembers(sys.modules[__name__], inspect.isfunction)
    menu = collections.OrderedDict(functions)
    while True:
        selection = lib.ask_question('Select a menu', answers=menu.keys())
        if selection == 'menu':
            break
        result = 'PASSED' if menu[selection]() == lib.PASS else 'FAILED'
        dash_length = len(selection) + 1 + len(result)
        log.info('-' * dash_length)
        log.info('{} {}'.format(selection, result))
        log.info('-' * dash_length)

    return lib.PASS


def power_cycle(conn=[], sw_cycle=False, delay_secs=30, retry=1, timeout=60):
    """Power Cycle

    As TDE, provide power cycle wrapper to power cycle uut for script use

    :param conn:
    :param sw_cycle:
    :param delay_secs:
    :param retry:
    :param timeout:
    :return:
    """
    userdict = lib.apdicts.userdict
    result = False

    while True:
        if sw_cycle:
            util.send(conn, 'reboot', timeout=timeout, expectphrase=rommon.prompt)
            result = True
        else:
            try:
                log.debug('Connections to power cycle: {}'.format(conn))
                for con in conn:
                    log.debug('Power Off {}'.format(str(con).split('|')[-1]))
                    con.power_off()
                    time.sleep(5)
                log.debug('Sleeping {} seconds'.format(max(delay_secs, delay_secs)))
                time.sleep(max(delay_secs, delay_secs))
                for con in conn:
                    log.debug('Power On {}'.format(str(con).split('|')[-1]))
                    con.power_on()
                    time.sleep(5)
                    con.waitfor('Escape character is *', regex=True)
                result = True
                log.info('Power cycle END')
                break

            except apexceptions.TimeoutException:
                # Handles failure to due to wrong terminal server IP address or slow network connection
                result = False
                log.warning('No response from console!')
                if retry >= 0:
                    question_result = util.ask_question(question='Check the network connection.',
                                                        lockname='Prompt Lock')
                    retry -= 1
                    if question_result:
                        continue
                break

    #  Specify Operator messgae
    if not result:
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Unit cannot boot'.format(util.whoami()),
            resolution_message='Check power cable',
        )
    return result


def power_off(conn='conn'):
    userdict = lib.apdicts.userdict
    userdict[conn].power_off()
    return lib.PASS


def erase_disk_in_rommon(skip_fail_pars_list=False, skip_fail=False):
    """Erase disk.

    As TDE, will define erase_disk_in_rommon so that test can erase disk.
    """
    userdict = lib.apdicts.userdict

    result = rommon.erase(
        userdict['conn'],
        'disk0:',
        timeout=1800,
        skip_fail_pars_list=skip_fail_pars_list,
        skip_fail=skip_fail,
    )
    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def show_idprom_in_rommon(skip_fail_pars_list=False, skip_fail=False):
    """Show idprom.

    As TDE, will define show_idprom_in_rommon so that test can show ipdrom and
    store it for later use.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'

    userdict['rommon']['idprom'] = rommon.show_idprom(userdict['conn'])

    # Check buffer for any key word failures
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = 'Fail'

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL
    return lib.PASS


def capture_uut_info_rommon(skip_fail=False):
    """capture uut info.

    As TDE, will define capture_uut_info_rommon so that test can grab sn, pid,
     and pn from rommon"""
    userdict = lib.apdicts.userdict
    result = 'Pass'

    while True:
        if not userdict['rommon']['idprom']['PCB S/N']:
            result = 'Fail'
            break
        else:
            userdict['sn'] = userdict['rommon']['idprom']['PCB S/N']
            log.info('SN captured: {}'.format(userdict['sn']))

        if not userdict['rommon']['idprom']['PCB P/N']:
            result = 'Fail'
            break
        else:
            userdict['pn'] = userdict['rommon']['idprom']['PCB P/N']
            log.info('PN captured: {}'.format(userdict['pn']))

        if not userdict['rommon']['idprom']['PCB Revision']:
            result = 'Fail'
            break
        else:
            userdict['rev'] = userdict['rommon']['idprom']['PCB Revision']
            log.info('PN Rev captured: {}'.format(userdict['rev']))
            userdict['pnrev'] = '{} {}'.format(userdict['pn'], userdict['rev'])
            break

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL
    return lib.PASS


def check_udi_enable(skip_fail=False):
    """Check UDI.

    As TDE, will define check_udi_enable so that test can verify product and
    version ID.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'

    # Make sure userdict['rommon']['idprom'] exist before doing check UDI enable
    if 'idprom' not in userdict['rommon']:
        userdict['rommon']['idprom'] = rommon.show_idprom(userdict['conn'])

    # TODO: make sure cesiumlib.verify_product_id_version_id is working
    try:
        log.info('SN:  {}'.format(userdict['rommon']['idprom']['Chassis S/N']))
        log.info('PID: {}'.format(userdict['rommon']['idprom']['Product ID']))
        log.info('VID: {}'.format(userdict['rommon']['idprom']['Version ID']))
        log.info('PN:  {}'.format(userdict['rommon']['idprom']['Top Assy P/N']))
        cesiumlib.verify_product_id_version_id(
            userdict['rommon']['idprom']['Chassis S/N'],
            userdict['rommon']['idprom']['Product ID'],
            userdict['rommon']['idprom']['Version ID'],
            userdict['rommon']['idprom']['Top Assy P/N'],
        )
    except apexceptions.ServiceFailure as error_message:
        result = 'Fail'
        log.warning(error_message)
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Invalid PIDVID'.format(util.whoami()),
            resolution_message='Call support',
        )
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def confreg(skip_fail_pars_list=False, skip_fail=False):
    """confreg

    As TDE, will define set_settings_in_rommon so that test set settings.
    """
    userdict = lib.apdicts.userdict

    result = rommon.confreg(userdict['conn'], '0x01', skip_fail_pars_list, skip_fail)

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def set_settings(skip_fail=False):
    """Set settings.

    As TDE, will define set_settings_in_rommon so that test set settings.
    """
    userdict = lib.apdicts.userdict
    userdict['operator_message'] = ''

    # Variables need to be all uppercase
    result = rommon.set_settings(
        userdict['conn'],
        ADDRESS=userdict['ip'],
        NETMASK=userdict['netmask'],
        GATEWAY=userdict['gateway'],
        SERVER=userdict['server'],
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']

    util.sleep(35, 5)

    return lib.PASS


def check_network(skip_fail_pars_list=False, skip_fail=False):
    """Check Network

    As TDE, will define set_settings_in_rommon so that test set settings.
    """
    userdict = lib.apdicts.userdict

    result = rommon.check_network(
        userdict['conn'],
        userdict['server'],
        timeout=35,
        skip_fail_pars_list=skip_fail_pars_list,
        skip_fail=skip_fail
    )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if not result and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def clear_settings(seq, reboot=True):
    clear_seq = seq.add_sequence(name='Clear ROMMON Settings')
    clear_seq.add_step(name='Boot Rommon', function=boot_rommon, kwargs={'reboot': reboot})
    clear_seq.add_step(name='Clear settings', function=clear_settings_in_rommon)


def clear_settings_in_rommon(skip_fail=False):
    """Clear settings.

    As TDE, will define clear_settings_in_rommon so that test clear settings.
    """
    userdict = lib.apdicts.userdict
    failure_count = 0
    if not rommon.confreg(userdict['conn'], '0x1'):
        log.error('Unable to set confreg to 0x1!')
        failure_count += 1
    rommon.clear_settings(userdict['conn'])
    userdict['rommon']['settings'] = rommon.get_settings(userdict['conn'])
    if '' != userdict['rommon']['settings']['ADDRESS']:
        log.error('ADDRESS needs to be ""!')
        failure_count += 1
    if '' != userdict['rommon']['settings']['SERVER']:
        log.error('SERVER needs to be ""!')
        failure_count += 1
    if '' != userdict['rommon']['settings']['GATEWAY']:
        log.error('GATEWAY needs to be ""!')
        failure_count += 1
    if '' != userdict['rommon']['settings']['IMAGE']:
        log.error('IMAGE needs to be ""!')
        failure_count += 1
    if '' != userdict['rommon']['settings']['CONFIG']:
        log.error('CONFIG needs to be ""!')
        failure_count += 1

    if failure_count:
        error_message = 'There are {} failures!'.format(failure_count)
        log.warning(error_message)
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message
        else:
            return lib.FAIL, error_message
    return lib.PASS


##################
# diag sequences #
##################
def mio_boot_diag(reboot=False, skip_fail_pars_list=False, skip_fail=False):
    """Boot diag.

    As TDE, will define boot_diag so that test can boot diag.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'

    if reboot:
        boot_rommon(reboot=reboot)

    # Config Rommon Network
    if not rommon.set_settings(
            userdict['conn'],
            ADDRESS=userdict['mio_ip'],
            GATEWAY=userdict['mio_gateway'],
            SERVER=userdict['server_ip'],
            NETMASK=userdict['mio_netmask'],
    ):
        result = 'Fail'

    # Check Rommon Network
    if not rommon.check_network(
            userdict['conn'],
            userdict['server_ip'],
            timeout=60,
            skip_fail_pars_list=skip_fail_pars_list,
            skip_fail=skip_fail,
    ):
        result = 'Fail'

    # Boot Diag
    if not 'Enter to activate this console' == rommon.boot(
        userdict['conn'],
        'tftp:{}'.format(userdict['diag_image']),
        'Enter to activate this console',
        timeout=300,
    ):
        result = 'Fail'

    if not userdict['diag']['prompt'] == util.sende(userdict['conn'], '\r', userdict['diag']['prompt']):
        result = 'Fail'

    # Check for Cavium Octeon NOT detected after send
    if 'NOT detected' in userdict['conn'].recbuf:
        error_message = 'Cavium Octeon NOT detected'
        log.warning(error_message)
        result = 'Fail'

    # Check for parsing after send
    if not util.fail_parsing_phase_chk(userdict['conn'].recbuf, skip_fail_pars_list=True):
        error_message = 'Error phrase found'
        log.warning(error_message)
        result = 'Fail'

    # Specify Operator messgae
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot boot diags'.format(util.whoami()),
            resolution_message='Call Support',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def check_system_leds():
    """Check System LEDs

    As TDE, will define check_system_leds so that operator can check LEDs light.
    """

    userdict = lib.apdicts.userdict
    result = 'Pass'

    util.sende(userdict['conn'], 'fanspeed led green\r', userdict['diag']['prompt'], timeout=5)
    util.sleep(1)
    # turn fan leds amber
    util.sende(userdict['conn'], 'fanspeed led amber\r', userdict['diag']['prompt'], timeout=5)
    util.sleep(1)
    while True:
        response = lib.ask_question(
            'Están los 4 FAN LEDs en la parte trasera encendidos color Ambar?.', ['YES', 'NO'])
        if 'YES' == response:
            log.info('{}'.format(response))
            break
        elif 'NO' == response:
            log.warning('{}'.format(response))
            result = 'Fail'
            userdict['operator_message'] = 'FAN LEDs in the back not colored Amber.'
            break
        else:
            continue

    # turn fan leds green
    util.sende(userdict['conn'], 'fanspeed led green\r', userdict['diag']['prompt'], timeout=5)
    util.sleep(1)
    while True:
        response = lib.ask_question(
            'Están los 4 FAN LEDs en la parte trasera encendidos color Verde?.', ['YES', 'NO'])
        if 'YES' == response:
            log.info('{}'.format(response))
            break
        elif 'NO' == response:
            log.warning('{}'.format(response))
            result = 'Fail'
            userdict['operator_message'] = 'FAN LEDs in the back not colored Green.'
            break
        else:
            continue

    # check front PS LEDs green
    while True:
        response = lib.ask_question(
            'Están los 2 PS LEDs en la parte delantera encendidos color Verde?.', ['YES', 'NO'])
        if 'YES' == response:
            log.info('{}'.format(response))
            break
        elif 'NO' == response:
            log.warning('{}'.format(response))
            result = 'Fail'
            userdict['operator_message'] = 'PS LEDs in the front not colored Green.'
            break
        else:
            continue

    # check Power On LED in each blade
    while True:
        response = lib.ask_question(
            'Está el LED de Encendido en cada Blade color Ambar o Verde?.', ['YES', 'NO'])
        if 'YES' == response:
            log.info('{}'.format(response))
            break
        elif 'NO' == response:
            log.warning('{}'.format(response))
            result = 'Fail'
            userdict['operator_message'] = 'Power On LED for each Blade not Amber or Green.'
            break
        else:
            continue

    # check Locate button LED
    while True:
        response = lib.ask_question(
            'Está el Locate LED encendido de cada Blade en color Azul?.', ['YES', 'NO']).upper()
        if 'YES' == response:
            log.info('{}'.format(response))
            break
        elif 'NO' == response:
            log.warning('{}'.format(response))
            result = 'Fail'
            userdict['operator_message'] = 'Locate LED Button for each Blade not Blue.'
            break
        else:
            continue

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail':
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def program_chassis_info(skip_fail=False):
    """Program Chassis Info

    As TDE, will define program_chassis_info so that test can program chassis.
    """

    userdict = lib.apdicts.userdict
    result = 'Pass'

    try:
        log.info('')
        log.info('Programming ...')
        log.info('')
        log.info('   SN    : [{}]'.format(userdict['sn']))
        log.info('   PID   : [{}]'.format(userdict['pid']))
        log.info('   VID   : [{}]'.format(userdict['vid']))
        log.info('   68PN  : [{}]'.format(userdict['pn']))
        log.info('   CLEI  : [{}]'.format(userdict[userdict['pn']]['uut_clei']))
        log.info('   FRUID : [{}]'.format(userdict['fru_id'][userdict['pid']]))

        userdict['conn'].send(text='\r', expectphrase=userdict['diag']['prompt'])
        # Serial Number
        userdict['conn'].send(text='i2c 0:51 -o19 -t ascii -w{}\r'.format(userdict['sn']),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # PID
        userdict['conn'].send(text='i2c 0:51 -o51 -t ascii -w{}\r'.format(userdict['pid']),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # VID
        userdict['conn'].send(text='i2c 0:51 -o84 -t ascii -w{}\r'.format(userdict['vid']),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # 68PN
        userdict['conn'].send(text='i2c 0:51 -o0C -t ascii -w{}\r'.format(userdict['pn']),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # CLEI
        userdict['conn'].send(text='i2c 0:51 -o88 -t ascii -w{}\r'.format(userdict[userdict['pn']]['uut_clei']),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # FRUID
        userdict['conn'].send(text='i2c 0:51 -o7C -t ascii -w{}\r'.format(userdict['fru_id'][userdict['pid']]),
                              expectphrase=userdict['diag']['prompt'], timeout=5)
        time.sleep(1)
        # Commit
        userdict['conn'].send(text='i2c 0:51 -c\r', expectphrase='done', timeout=5)
    except KeyError as error_message:
        result = 'Fail'
        log.error('Dictionary Key "{}" not found.'.format(error_message))

    userdict['conn'].send(text='\r', expectphrase=userdict['diag']['prompt'], timeout=5)

    # Check Chassis Info
    userdict['conn'].send(text='i2c 0:51 -a0\r')
    matches = []
    while True:
        userdict['conn'].waitfor(expectphrase=['>',
                                               userdict['diag']['prompt']], timeout=5)
        matches.extend(re.findall('\[(.*)\] >', userdict['conn'].recbuf))
        if '>' == userdict['conn'].foundphrase:
            userdict['conn'].send('\r')
            continue
        elif userdict['diag']['prompt'] == userdict['conn'].foundphrase:
            break

    log.info('')
    log.info('Checking Info ...')
    log.info('')
    tmp_str = 'Field(s): '

    log.info('   - Field     : CHASSIS SERIAL NUMBER')
    log.info('      Found    : [{}]'.format(matches[13]))
    log.info('      Expected : [{}]'.format(userdict['sn']))
    if matches[13] != userdict['sn']:
        result = 'Fail'
        tmp_str = tmp_str + 'CHASSIS SERIAL NUMBER, '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    log.info('')
    log.info('   - Field     : PRODUCT NAME / PID')
    log.info('      Found    : [{}]'.format(matches[25]))
    log.info('      Expected : [{}]'.format(userdict['pid']))
    if matches[25] != userdict['pid']:
        result = 'Fail'
        tmp_str = tmp_str + 'PRODUCT NAME /PID , '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    log.info('')
    log.info('   - Field     : VERSION ID')
    log.info('      Found    : [{}]'.format(matches[35]))
    log.info('      Expected : [{}]'.format(userdict['vid']))
    if matches[35] != userdict['vid']:
        result = 'Fail'
        tmp_str = tmp_str + 'VERSION ID , '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    log.info('')
    log.info('   - Field     : TAN PART NUM')
    log.info('      Found    : [{}]'.format(matches[11]))
    log.info('      Expected : [{}]'.format(userdict['pn']))
    if matches[11] != userdict['pn']:
        result = 'Fail'
        tmp_str = tmp_str + 'TAN PART NUM , '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    log.info('')
    log.info('   - Field     : CLEI Code')
    log.info('      Found    : [{}]'.format(matches[37]))
    log.info('      Expected : [{}]'.format(userdict[userdict['pn']]['uut_clei']))
    if matches[37] != userdict[userdict['pn']]['uut_clei']:
        result = 'Fail'
        tmp_str = tmp_str + 'CLEI Code , '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    log.info('')
    log.info('   - Field     : FRU File ID')
    log.info('      Found    : [{}]'.format(matches[31]))
    log.info('      Expected : [{}]'.format(userdict['fru_id'][userdict['pid']]))
    if matches[31] != userdict['fru_id'][userdict['pid']]:
        result = 'Fail'
        tmp_str = tmp_str + 'FRU File ID , '
        log.error('      Result   : Fail!')
    else:
        log.info('      Result   : Ok!')

    if len(tmp_str) > 10:
        userdict['operator_message'] = tmp_str[:-2] + ' not programmed correctly.'

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and skip_fail:
        userdict['failed_sequences'][util.whoami()] = userdict['operator_message']

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def format_bootflash():
    """Format Bootflash

    AS TDE, will define format_bootflash so that test can erase content in bootflash.
    """

    userdict = lib.apdicts.userdict

    userdict['conn'].send(text='\r', expectphrase=userdict['diag']['prompt'], timeout=5)
    # Set Network from Diags
    userdict['conn'].send(text='source setip {}\r'.format(userdict['mio_ip']))

    while True:
        userdict['conn'].waitfor(expectphrase=['is Alive', userdict['diag']['prompt']], timeout=10)

        if 'is Alive' in userdict['conn'].foundphrase:
            log.info('- Ping Successful.')
        elif userdict['diag']['prompt'] in userdict['conn'].foundphrase:
            break

    userdict['conn'].send(
        text='scp gen-apollo@{}://tftpboot/fdisk128g.sh /pad/bks/tools\r'.format(userdict['server_ip']),
        expectphrase=['(yes/no)?', 'password'], timeout=30)
    if '(yes/no)?' == userdict['conn'].foundphrase:
        userdict['conn'].send(text='yes\r', expectphrase='password')

    userdict['conn'].send(text='Ad@pCr01!\r', expectphrase='#')

    if 'No such file or directory' in userdict['conn'].recbuf:
        return lib.FAIL, 'No such file or directory.'

    userdict['conn'].send(text='chmod u+x /pad/bks/tools/fdisk128g.sh\r', expectphrase='#', timeout=30)
    userdict['conn'].send(text='umount /bootflash\r', expectphrase='#')
    userdict['conn'].send(text='/pad/bks/tools/fdisk128g.sh /dev/sda\r', expectphrase='[yes|no]', timeout=30)
    userdict['conn'].send(text='yes\r', expectphrase='All done with partitions and formatting.', timeout=120)
    userdict['conn'].send(text='mount /dev/sda3 /bootflash\r', expectphrase='#', timeout=30)

    return lib.PASS


################
# OS sequences #
################
def boot_os(reboot=False, skip_fail=False):
    """Boot OS.

    As TDE, will define boot_os so that test can boot OS.
    """
    userdict = lib.apdicts.userdict
    result = 'Pass'

    if reboot:
        boot_rommon(reboot=reboot)

    # Boot Kickstart
    rommon.boot(
        userdict['conn'],
        'tftp:{}'.format(userdict['base_kickstart_image']),
        expectphrase=['switch\(boot\)#'],
        timeout=300,
    )

    # Set Network
    userdict['conn'].send(text='\r', expectphrase='switch(boot)#', timeout=5)
    userdict['conn'].send(text='start\r', expectphrase='#')

    userdict['conn'].send(text='ifconfig eth0 {} netmask {} up\r'.format(userdict['mio_ip'], userdict['mio_netmask']),
                          expectphrase='#')
    userdict['conn'].send(text='route add default gw {}\r'.format(userdict['mio_gateway']), expectphrase='#')
    retry = 0
    while True:
        userdict['conn'].send(text='ping {} -c5\r'.format(userdict['mio_gateway']), expectphrase='#', timeout=10)
        if '5 received' in userdict['conn'].recbuf:
            break
        else:
            if retry == 3:
                return lib.FAIL, 'Ping failed!'
            else:
                retry += 1
    userdict['conn'].send(text='exit\r', expectphrase='switch(boot)#')

    # Copy Images to Bootflash
    userdict['conn'].send(text='mkdir bootflash:/mfg\r', expectphrase='switch(boot)#', timeout=5)
    copy_file_to_uut([userdict['base_manager_image'], userdict['base_system_image']],
                     'bootflash:/mfg',
                     userdict['conn'],
                     'BS.kick')

    # Load Customer Image
    userdict['conn'].send(text='delete bootflash:nuova-sim-mgmt-nsg.0.1.0.001.bin\r',
                          expectphrase='switch(boot)#',
                          timeout=5)
    userdict['conn'].send(text='copy bootflash:mfg/{} '
                               'bootflash:nuova-sim-mgmt-nsg.0.1.0.001.bin\r'.format(userdict['base_manager_image']),
                          expectphrase='switch(boot)#')
    time.sleep(15)
    util.sende(userdict['conn'], text='load bootflash:/mfg/{}\r'.format(userdict['base_system_image']))

    # OS Configuration
    while True:
        userdict['conn'].waitfor(expectphrase=['(setup/restore)',
                                               'Continue? (y/n)',
                                               'Enforce strong password? (y/n)',
                                               'Enter the password for "admin"',
                                               'Confirm the password for "admin"',
                                               'Enter the system name',
                                               'Physical Switch Mgmt0 IP address',
                                               'Physical Switch Mgmt0 IPv4 netmask',
                                               'IPv4 address of the default gateway',
                                               'Supervisor Mgmt IP address',
                                               'Supervisor Mgmt IPv4 netmask',
                                               'Do you want to configure IP block for ssh access',
                                               'Do you want to configure IP block for https access',
                                               'Configure the DNS Server IP address',
                                               'Configure the default domain name',
                                               'Apply and save the configuration',
                                               'login:'], timeout=300)

        if '(setup/restore)' == userdict['conn'].foundphrase or \
                'Do you want to configure IP block for ssh access' == userdict['conn'].foundphrase or \
                'Do you want to configure IP block for https access' == userdict['conn'].foundphrase or \
                'Configure the DNS Server IP address' == userdict['conn'].foundphrase or \
                'Configure the default domain name' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='\r')
        elif 'Continue? (y/n)' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='y\r')
        elif 'Enforce strong password? (y/n)' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='n\r')
        elif 'Enter the password for "admin"' == userdict['conn'].foundphrase or \
                'Confirm the password for "admin"' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='{}\r'.format(userdict['os']['admin_password']))
        elif 'Enter the system name' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='mio\r')
        elif 'Physical Switch Mgmt0 IP address' == userdict['conn'].foundphrase or \
                'Supervisor Mgmt IP address' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='{}\r'.format(userdict['mio_ip']))
        elif 'Physical Switch Mgmt0 IPv4 netmask' == userdict['conn'].foundphrase or \
                'Supervisor Mgmt IPv4 netmask' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='{}\r'.format(userdict['mio_netmask']))
        elif 'IPv4 address of the default gateway' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='{}\r'.format(userdict['mio_gateway']))
        elif 'Apply and save the configuration' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='yes\r', expectphrase='login:')
            break
        elif 'login:' == userdict['conn'].foundphrase:
            break
        else:
            return lib.FAIL, "Something went wrong! Call Cisco TDE."

    # OS Login
    userdict['conn'].send(text='\r')
    while True:
        userdict['conn'].waitfor(expectphrase=['ogin:',
                                               'assword:',
                                               '-A#'], timeout=30)

        if 'ogin:' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='admin\r')
        elif 'assword:' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='{}\r'.format(userdict['os']['admin_password']))
        elif '-A#' == userdict['conn'].foundphrase:
            userdict['conn'].send(text='terminal length 0\r', expectphrase='-A#')
            userdict['conn'].send(text='terminal session-timeout 0\r', expectphrase='-A#')
            time.sleep(30)
            fxos_scope('security', True)
            fxos_scope('default-auth')
            userdict['conn'].send(text='set refresh-period 60\r', expectphrase='default-auth\*? #', regex=True)
            userdict['conn'].send(text='set session-timeout 60\r', expectphrase='default-auth\*? #', regex=True)
            userdict['conn'].send(text='commit-buffer\r', expectphrase='default-auth #')
            userdict['conn'].send(text='top\r', expectphrase='-A#')
            # Check Operability State
            timeout = time.time() + 120
            while True:
                time.sleep(10)
                userdict['conn'].send(text='show fabric-interconnect detail\r', expectphrase='-A#')
                operability_state = re.findall('Operability: ?(.*)\r', userdict['conn'].recbuf)
                if 'Operable' in operability_state:
                    break
                else:
                    if time.time() > timeout:
                        return lib.FAIL, 'System is not Operable!'
                    else:
                        continue
            break
        else:
            return lib.FAIL, "Something went wrong! Call Cisco TDE."

    # OS Network Setup
    fxos_scope('fabric-interconnect a', True)

    userdict['conn'].send(text='set out-of-band ip {} netmask {} gw {}\r'.format(userdict['mio_ip'],
                                                                                 userdict['mio_netmask'],
                                                                                 userdict['mio_gateway']),
                          expectphrase='fabric-interconnect #', timeout=10)
    userdict['conn'].send(text='commit-buffer\r', expectphrase='fabric-interconnect #')

    userdict['conn'].send(text='end\r', expectphrase='-A#', timeout=10)
    userdict['conn'].send(text='connect local-mgmt\r', expectphrase='-A(local-mgmt)#')

    retry = 0
    while True:
        userdict['conn'].send(text='ping {} count 5\r'.format(userdict['mio_gateway']),
                              expectphrase='-A(local-mgmt)#', timeout=30)
        if '5 received' in userdict['conn'].recbuf:
            break
        else:
            if retry >= 3:
                return lib.FAIL, 'No ping!'
            else:
                retry += 1
                continue

    userdict['conn'].send(text='exit\r', expectphrase='-A#')

    # Specify Operator message
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - Cannot boot OS'.format(util.whoami()),
            resolution_message='Call support',
        )

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def verify_licenses_in_os(skip_fail=False):
    """Verify licenses.

    As TDE, will define verify_licenses_in_os so that test can verify customer
    ordered licenses.
    """
    userdict = lib.apdicts.userdict
    conn = userdict['conn']
    result = 'Pass'

    util.sende(conn, 'show version\r', expectphrase='ciscoasa#', timeout=50, retry=2)
    if not util.fail_parsing_phase_chk(conn.recbuf, skip_fail_pars_list=True):
        result = 'Fail'

    # get default license features
    userdict['recbuf'] = conn.recbuf

    # Verify license features
    start_field = 'Licensed features for this platform:'
    end_field = 'Serial Number'
    start_field_num = userdict['recbuf'].index(start_field)
    end_field_num = userdict['recbuf'].index(end_field)
    buff_features = userdict['recbuf'][start_field_num:end_field_num]
    log.info('buff features: {}'.format(buff_features))

    exclude_cmpd = ['Licensed features for this platform']
    buff_features_dic = util.buff_to_dict(buff_features, exclude_cmpd)
    log.info('buff features: {}'.format(buff_features_dic))

    userdict['ref_features'] = userdict['buff_features_def_dic']
    bad = {}
    for item in buff_features_dic:
        if userdict['ref_features'][item] != buff_features_dic[item]:
            log.info('-BAD! -item: {}, UUT features: {}, Reference features: {}'.format(
                item, buff_features_dic[item], userdict['ref_features'][item])
            )
            bad[item] = [buff_features_dic[item], userdict['ref_features'][item]]
        else:
            log.info('-OK! Item {}, UUT features: {}, Reference features: {}'.format(
                item, buff_features_dic[item], userdict['ref_features'][item])
            )

    if len(bad) > 0:
        result = 'Fail'

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    # Specify Operator messgae
    if result == 'Fail':
        userdict['operator_message'] = util.operator_message(
            error_message='Error: {} - License features'.format(util.whoami()),
            resolution_message='Call support',
        )

    if result == 'Fail' and not skip_fail:
        return lib.FAIL, userdict['operator_message']
    return lib.PASS


def record_genealogy():
    """Record genealogy.

    As TDE, will define record_genealogy so that test can record UUT genelogy.
    """
    userdict = lib.apdicts.userdict
    genealogy = [(
        {
            'serial_number': userdict['sn'],
            'product_id': userdict['pid'],
        },
        {
            'serial_number': 'JMXCHILD001',
            'product_id': 'FPR9K-SUP=',
            # 'location':
            # {
            #     'ulocation': 'loc1',
            # },
        },
    )]

    genealogy2 = [[(
        {
            'serial_number': 'X_SN',
            'product_id': 'X_PID',
        },
        {
            'serial_number': 'Y_SN',
            'product_id': 'Y_PID',
            'location':
            {
                'ulocation': 'loc2'
            },
        },
    ), (
        {
            'serial_number': 'X_SN',
            'product_id': 'X_PID',
        },
        {
            'serial_number': 'Z_SN',
            'product_id': 'Z_PID',
        },
    )], [(
        {
            'serial_number': 'XX_SN',
            'product_id': 'XX_PID',
        },
        {
            'serial_number': 'YY_SN',
            'product_id': 'YY_PID',
        },
    ), (
        {
            'serial_number': 'YY_SN',
            'product_id': 'YY_PID',
        },
        {
            'serial_number': 'ZZ_SN',
            'product_id': 'ZZ_PID',
            'location':
            {
                'slot': 'loc1'
            },
        },
    )]]
    log.critical('genealogy in:  {}'.format(genealogy))
    log.critical('genealogy in:  {}'.format(genealogy2))
    cesiumlib.register_genealogy(genealogy, 'ASSEMBLE')
    log.critical('genealogy out:  {}'.format(cesiumlib.get_genealogy(userdict['sn'], userdict['pid'])))
    return lib.PASS


def fxos_scope(command, top_level=False):
    """FXOS Scope

    This routine will issue the scope command and set the expect_prompt.
    """
    userdict = lib.apdicts.userdict

    if 'scope' not in command:
        command = 'scope {}'.format(command)

    if top_level:
        userdict['conn'].send(text='end\r', expectphrase='-A#', timeout=5)

    retry = 0
    while True:
        if retry >= 3:
            raise Exception('Command not working after [{}] retries ...'.format(retry))
        userdict['conn'].send(text='\r', expectphrase='#')
        userdict['conn'].sende(text='{}\r'.format(command))
        userdict['conn'].waitfor(expectphrase=['{} #'.format(command.split(' ')[1]),
                                               'Software Error',
                                               'Error: Managed object does not exist'], timeout=10)

        if '{} #'.format(command.split(' ')[1]) == userdict['conn'].foundphrase or \
                'Error: Managed object does not exist' == userdict['conn'].foundphrase:
            break
        else:
            retry += 1
            log.info('   - Retry [{}] command [{}] ...'.format(retry, command))
            time.sleep(30)

    return lib.PASS


def fxos_install_bundle_image(expected_version, timeout, force_install=False):

    userdict = lib.apdicts.userdict

    fxos_scope('firmware', True)

    userdict['conn'].send(text='show version\r', expectphrase='firmware #')
    installed_version = re.findall('System version: ?(.*)\r', userdict['conn'].recbuf)[0]

    log.info('   - Installed Version : [{}]'.format(installed_version))
    log.info('   - New Version       : [{}]'.format(expected_version))

    if expected_version == installed_version and not force_install:
        log.info('New Version is already installed [{}].'.format(expected_version))
    else:
        fxos_scope('auto-install')
        userdict['conn'].send(text='install platform platform-vers {}\r'.format(expected_version),
                              expectphrase='Do you want to proceed? (yes/no):',
                              timeout=120)
        userdict['conn'].send(text='yes\r')
        while True:
            userdict['conn'].waitfor(expectphrase=['Do you want to proceed? (yes/no):',
                                                   'Firmware Package with version {} is not available'.format(
                                                       expected_version),
                                                   'Triggering Install-Platform',
                                                   'login:'],
                                     timeout=360)

            if 'Do you want to proceed? (yes/no):' == userdict['conn'].foundphrase:
                userdict['conn'].send(text='yes\r')
            elif 'Firmware Package with version {} is not available'.format(expected_version) == \
                    userdict['conn'].foundphrase:
                raise Exception('Version [{}] not available. Please check!'.format(expected_version))
            elif 'Triggering Install-Platform' == userdict['conn'].foundphrase:
                log.info('')
                log.info('- Got [{}]'.format(userdict['conn'].foundphrase))
                # Wait for Reboot or Soft Reboot
                try:
                    userdict['conn'].waitfor(expectphrase=['Rommon image verified successfully'], timeout=900)
                    log.info('- Got [{}]'.format(userdict['conn'].foundphrase))
                    userdict['conn'].send(text='\r')
                    continue
                except Exception:
                    log.info('   - Shutdown timed out, trying soft reboot ...')
                    # Soft Reboot
                    userdict['conn'].send(text='\r', expectphrase='login:', timeout=10)
                    userdict['conn'].send(text='admin\r', expectphrase='Password:')
                    userdict['conn'].send(text='{}\r'.format(userdict['os']['admin_password']), expectphrase='-A#')
                    userdict['conn'].send(text='connect local-mgmt\r', expectphrase='(local-mgmt)#')
                    userdict['conn'].send(text='reboot\r', expectphrase='Do you still want to reboot? (yes/no)')
                    userdict['conn'].send(text='yes\r')
                    userdict['conn'].waitfor(expectphrase=['Rommon image verified successfully'], timeout=900)
                    continue
            elif 'login:' == userdict['conn'].foundphrase:
                userdict['conn'].send(text='admin\r', expectphrase='Password:')
                userdict['conn'].send(text='{}\r'.format(userdict['os']['admin_password']), expectphrase='-A#')
                userdict['conn'].send(text='terminal length 0\r', expectphrase='-A#')
                userdict['conn'].send(text='terminal session-timeout 0\r', expectphrase='-A#')
                break
            else:
                raise Exception('Something went wrong!')

        # Check Installation every 30 secs until TIMEOUT
        fxos_scope('system', True)
        retry = 0
        while True:
            userdict['conn'].send(text='show firmware monitor\r', expectphrase='system #')
            upgrade_status = re.findall('Upgrade-Status: ?(.*)\r', userdict['conn'].recbuf)

            log.info('')
            log.info('FPRM                  - [{}]'.format(upgrade_status[0]))
            log.info('Fabric Interconnect A - [{}]'.format(upgrade_status[1]))
            log.info('Chassis:Server        - [{}]'.format(upgrade_status[2]))

            if upgrade_status.count('Ready') == 3:
                break
            else:
                if retry <= 3:
                    log.info('   Waiting 30 secs ...')
                    time.sleep(30)
                    retry += 1
                    continue
                else:
                    raise Exception('Upgrade did not finish completely.')

    return lib.PASS


def check_fw_platform_pack(skip_fail=False):
    """Check FW Platform Pack

    This routine will check if firmware platform pack is set correctly.
    """
    userdict = lib.apdicts.userdict
    conn = userdict['conn']
    result = 'Pass'
    error_message = ''

    # <-- CODE HERE
    fxos_scope('org', True)
    fxos_scope('fw-platform-pack default', False)

    conn.send(text='show detail\r', expectphrase='fw-platform-pack #', timeout=10)
    installed_package_version = re.findall('Platform Bundle Version: ?(.*)\r', userdict['conn'].recbuf)[0]
    expected_package_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_package_version']

    log.info('')
    log.info('Installed FW Platform Pack : [{}]'.format(installed_package_version))
    log.info('Expected  FW Platform Pack : [{}]'.format(expected_package_version))

    if installed_package_version != expected_package_version:
        result = 'Fail'
        error_message = 'Incorrect Firmware Platform Pack'
    # CODE HERE -- >

    util.test_result_log(
        serial_num=userdict['sn'],
        uut_type=userdict['pid'],
        result=result,
        test_name=lib.getstepdata()['stepdict']['name'],
        test_area=userdict['area'],
        comment='Skipped Fail' if skip_fail and not result else '',
        loop_cnt=userdict['iterations'],
    )

    if result == 'Fail':
        if skip_fail:
            userdict['failed_sequences'][util.whoami()] = error_message
        else:
            userdict['operator_message'] = util.operator_message(
                error_message=error_message,
                resolution_message='Call support',
            )
            return lib.FAIL, userdict['operator_message']
    return lib.PASS


def discover_servers():
    """Discover Servers

     Will identify slots with server populated.
     """
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    conn.send(text='\r', expectphrase=['-A#', 'login:', 'pack #'])
    if 'login:' == conn.foundphrase:
        conn.send(text='admin\r', expectphrase='assword:')
        conn.send(text='cisco123\r', expectphrase='-A#')
    elif 'pack #' == conn.foundphrase:
        conn.send(text='end\r', expectphrase='-A#')

    # <-- CODE HERE
    active_servers = []
    for server in range(userdict['max_server_num']):
        fxos_scope('server 1/{}'.format(server + 1), True)
        conn.send(text='\r')
        conn.waitfor(expectphrase=['server #',
                                   '-A#'], timeout=10)
        if '-A#' == conn.foundphrase:
            continue
        elif 'server #' == conn.foundphrase:
            conn.send(text='show detail\r', expectphrase='server #')
            try:
                slot = re.findall('Slot: ?(.*)\r', conn.recbuf)[0]
                active_servers.extend([slot])
            except IndexError:
                continue
        else:
            raise Exception('Something went wrong!')

    userdict['active_servers'] = active_servers

    return lib.PASS


def check_servers_operational_state():

    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    for server in userdict['active_servers']:
        log.info('')
        log.info('- Operational Status for server 1/{} :'.format(server))
        op_state_ack = False
        op_state_init = False

        timeout = time.time() + 1200
        while True:
            fxos_scope('server 1/{}'.format(server))
            conn.send(text='show detail\r', expectphrase='server #')

            overall_status = re.findall('Overall Status: ?(.*)\r', conn.recbuf)[0]
            association_status = re.findall('Association: ?(.*)\r', conn.recbuf)[0]
            discovery_status = re.findall('Discovery: ?(.*)\r', conn.recbuf)[0]

            log.info('   - Overall Status    : [{}]'.format(overall_status))
            log.info('   - Association       : [{}]'.format(association_status))
            log.info('   - Discovery         : [{}]'.format(discovery_status))

            if overall_status == 'Compute Mismatch' and not op_state_ack:
                fxos_scope('chassis 1', True)
                conn.send(text='acknowledge slot {}\r'.format(server), expectphrase='chassis\*? #', regex=True)
                conn.send(text='commit-buffer\r', expectphrase='chassis #')
                op_state_ack = True
                time.sleep(60)
                continue
            elif overall_status != 'Ok':
                if time.time() > timeout:
                    raise Exception('Server [{}] Overall Status timed out, '
                                    'did not reach "Ok" status.'.format(server))
                else:
                    log.info("      - Overall Status is not 'Ok', retrying in 60 secs ...")
                    log.info('')
                    time.sleep(60)
                    continue

            if association_status != 'Associated':
                if time.time() > timeout:
                    raise Exception('Server [{}] Association timed out, '
                                    'did not reach "Associated" status'.format(server))
                else:
                    log.info("      - Association is not 'Associated', retrying in 60 secs ...")
                    log.info('')
                    time.sleep(60)
                    continue

            if discovery_status != 'Complete':
                if time.time() > timeout:
                    raise Exception('Server [{}] Discovery timed out, '
                                    'did not reach "Complete" status'.format(server))
                else:
                    log.info("      - Discovery is not 'Complete', retrying in 60 secs ...")
                    log.info('')
                    time.sleep(60)
                    continue

            break

        fxos_scope('server 1/{}'.format(server), True)
        conn.send(text='show inventory expand\r', expectphrase='server #')
        log.info('')

        timeout = time.time() + 1200
        while True:

            fxos_scope('ssa', True)
            fxos_scope('slot {}'.format(server), False)
            conn.send(text='show detail\r', expectphrase='slot #')

            operational_state = re.findall('Operational State: ?(.*)\r', conn.recbuf)[0]
            disk_state = re.findall('Disk State: ?(.*)\r', conn.recbuf)[0]

            log.info('   - Operational State : [{}]'.format(operational_state))
            log.info('   - Disk State        : [{}]'.format(disk_state))

            if operational_state != 'Online':
                if time.time() > timeout:
                    raise Exception('Server [{}] Operational State timed out, '
                                    'did not reach "Online" status'.format(server))
                else:
                    log.info("      - Operational State is not 'Online', retrying in 60 secs ...")
                    log.info('')
                    time.sleep(60)
                    continue

            if disk_state == 'Token Mismatch' and not op_state_init:
                conn.send(text='reinitialize\r', expectphrase='slot\*? #', regex=True)
                conn.send(text='commit-buffer\r', expectphrase='slot #')
                op_state_init = True
                time.sleep(60)
                continue
            elif disk_state != 'Ok':
                if time.time() > timeout:
                    raise Exception('Server [{}] Disk State timed out, '
                                    'did not reach "Ok" status.'.format(server))
                else:
                    log.info("      - Disk State is not 'Ok', retrying in 60 secs ...")
                    log.info('')
                    time.sleep(60)
                    continue

            break

    return lib.PASS


def check_fabric_interconnect_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    fxos_scope('fabric-interconnect a', True)
    conn.send(text='show detail\r', expectphrase='interconnect #', timeout=10)
    mio_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
    mio_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
    mio_vid = re.findall('VID: ?(.*)\r', conn.recbuf)[0]
    log.info('   - Fabric Interconnect Serial Number : [{}]'.format(mio_sernum))
    log.info('   - Fabric Interconnect PID           : [{}]'.format(mio_pid))
    log.info('   - Fabric Interconnect VID           : [{}]'.format(mio_vid))
    # Check fabric SN and PID
    found = False
    for item in userdict['genealogy']:
        if mio_sernum == item['serial_number'] and '{}='.format(mio_pid) == item['product_id']:
            found = True
            log.info('      + Fabric Interconnect SN [{}] and '
                     'PID [{}] found in genealogy record.'.format(item['serial_number'], item['product_id']))
            break
    if not found:
        return lib.FAIL, 'Fabric Interconnect PID [{}] with ' \
                         'SN [{}] not found in genealogy record.'.format(mio_pid, mio_sernum)
    # Check Fabric VID
    test_record = get_legacy_tst_record(serial_number=mio_sernum, areas=['SYSASSY'], test_status='P')
    if mio_vid == test_record['hwrev']:
        log.info('      + Fabric Interconnect VID [{}] found in tst_record.'.format(test_record['hwrev']))
    else:
        return lib.FAIL, 'Fabric Interconnect VID [{}] not found in tst_record.'.format(mio_vid)

    # Add MIO PID to found_hw
    add_to_found_hw(mio_pid, 1)

    return lib.PASS


def check_network_module_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    network_module = 2
    while network_module <= userdict['max_network_module_num']:
        fxos_scope('fabric-interconnect a', True)
        fxos_scope('card {}'.format(network_module), False)

        conn.send(text='\r', expectphrase=['interconnect #', 'card #'], timeout=10)

        if conn.foundphrase == 'card #':
            conn.send(text='show detail\r', expctphrase='card #')
            network_mod_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
            network_mod_pid = re.findall('Model: ?(.*)\r', conn.recbuf)[0]

            log.info('   - Network Module : [{}]'.format(network_module))
            log.info('      SN  : [{}]'.format(network_mod_sernum))
            log.info('      PID : [{}]'.format(network_mod_pid))

            # Check SN and PID
            found = False
            for item in userdict['genealogy']:
                if network_mod_sernum == item['serial_number'] and '{}='.format(network_mod_pid) == item['product_id']:
                    found = True
                    log.info('         + Network Module [{}] SN [{}] and '
                             'PID [{}] found in genealogy record.'.format(network_module,
                                                                          item['serial_number'],
                                                                          item['product_id']))
                    break
            if not found:
                return lib.FAIL, 'Network Module [{}] PID [{}] with ' \
                                 'SN [{}] not found in genealogy record.'.format(network_module,
                                                                                 network_mod_pid,
                                                                                 network_mod_sernum)
            # Check Network Module Authenticity
            conn.send(text='show fault detail\r', expectphrase='card #')
            network_mod_fault_cause = re.findall('Cause: ?(.*)\r', conn.recbuf)

            if not network_mod_fault_cause:
                log.info('      Network Module [{}] ACT2 Check OK!'.format(network_module))
            else:
                return lib.FAIL, 'Network Module [{}] failed for "{}".'.format(network_module, network_mod_fault_cause)

            # Add Ntework Module PID not userdict['found_hw']
            add_to_found_hw(network_mod_pid, 1)

        network_module += 1

    return lib.PASS


def check_chassis_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    fxos_scope('chassis 1', True)
    conn.send(text='show detail\r', expectphrase='chassis #')
    chassis_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
    chassis_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
    chassis_vid = re.findall('VID: ?(.*)\r', conn.recbuf)[0]

    log.info('   - Chassis Serial Number : [{}]'.format(chassis_sernum))
    log.info('   - Chassis PID           : [{}]'.format(chassis_pid))
    log.info('   - Chassis VID           : [{}]'.format(chassis_vid))

    if chassis_sernum == userdict['sn']:
        log.info('      + Chassis SN  OK!')
    else:
        return lib.FAIL, 'Chassis Serial Number found [{}] expected [{}].'.format(chassis_sernum, userdict['sn'])

    if chassis_pid == userdict['pid']:
        log.info('      + Chassis PID OK!')
    else:
        return lib.FAIL, 'Chassis PID found [{}] expected [{}].'.format(chassis_pid, userdict['pid'])

    if chassis_vid == userdict['vid']:
        log.info('      + Chassis VID OK!')
    else:
        return lib.FAIL, 'Chassis VID found [{}] expected [{}].'.format(chassis_vid, userdict['vid'])

    # Add Chassis PID to userdict['found_hw']
    add_to_found_hw(chassis_pid, 1)

    return lib.PASS


def check_psu_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    psu_num = 1
    while psu_num <= userdict['max_psu_num']:
        fxos_scope('chassis 1', True)
        fxos_scope('psu {}'.format(psu_num), False)

        conn.send(text='\r', expectphrase=['chassis #', 'psu #'])

        if 'psu #' == conn.foundphrase:
            conn.send(text='show detail\r', expectphrase='psu #')
            psu_presence = re.findall('Presence: ?(.*)\r', conn.recbuf)[0]
            psu_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
            psu_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
            psu_pn = re.findall('Part Number: ?(.*)\r', conn.recbuf)[0]
            psu_vid = re.findall('VID: ?(.*)\r', conn.recbuf)[0]

            log.info('   - PSU : [{}]'.format(psu_num))
            log.info('      Presence      : [{}]'.format(psu_presence))
            log.info('      Serial Number : [{}]'.format(psu_sernum))
            log.info('      Part Number   : [{}]'.format(psu_pn))
            log.info('      PID           : [{}]'.format(psu_pid))
            log.info('      VID           : [{}]'.format(psu_vid))

            # Check PSU Presence
            if psu_presence == 'Equipped':
                log.info('         + PSU [{}] presence OK!'.format(psu_num))
            else:
                return lib.FAIL, 'PSU [{}] presence found [{}] expected "Equipped".'.format(psu_num, psu_presence)
            # Check PSU SN and PID
            found = False
            for item in userdict['genealogy']:
                if psu_sernum == item['serial_number'] and '{}='.format(psu_pid) == item['product_id']:
                    found = True
                    log.info('         + PSU SN [{}] and PID [{}]'
                             ' found in genealogy record.'.format(item['serial_number'], item['product_id']))
                    break
            if not found:
                return lib.FAIL, 'PSU PID [{}] with ' \
                                 'SN [{}] not found in genealogy record.'.format(psu_pid, psu_sernum)
            # Check PSU PN
            test_record = get_legacy_tst_record(serial_number=psu_sernum, areas=['SYSASSY'], test_status='P')
            if psu_pn == test_record['tan']:
                log.info('         + PSU PN [{}] found in tst_record.'.format(test_record['tan']))
            else:
                return lib.FAIL, 'PSU PN [{}] not found in tst_record.'.format(psu_pn)
            # Check PSU VID
            if psu_vid == test_record['hwrev']:
                log.info('         + PSU VID [{}] found in tst_record.'.format(test_record['hwrev']))
            else:
                return lib.FAIL, 'PSU VID [{}] not found in tst_record.'.format(psu_vid)

            # Add PSU PID to userdict['found_hw']
            add_to_found_hw(psu_pid, 1)
            log.info('')
        psu_num += 1

    return lib.PASS


def check_fan_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    fan_num = 1
    while fan_num <= userdict['max_fan_num']:
        fxos_scope('chassis 1', True)
        fxos_scope('fan-module 1 {}'.format(fan_num), False)

        conn.send(text='\r', expectphrase=['chassis #', 'fan-module #'])

        if 'fan-module #' == conn.foundphrase:
            conn.send(text='show detail\r', expectphrase='fan-module #')
            fan_presence = re.findall('Presence: ?(.*)\r', conn.recbuf)[0]
            fan_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
            fan_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
            fan_pn = re.findall('Part Number: ?(.*)\r', conn.recbuf)[0]
            fan_vid = re.findall('VID: ?(.*)\r', conn.recbuf)[0]

            log.info('   - FAN [{}]'.format(fan_num))
            log.info('      Presence    : [{}]'.format(fan_presence))
            log.info('      SN          : [{}]'.format(fan_sernum))
            log.info('      Part Number : [{}]'.format(fan_pn))
            log.info('      PID         : [{}]'.format(fan_pid))
            log.info('      VID         : [{}]'.format(fan_vid))

            # Check FAN Presence
            if fan_presence == 'Equipped':
                log.info('         + FAN [{}] presence OK!'.format(fan_num))
            else:
                return lib.FAIL, 'FAN [{}] presence found [{}] expected "Equipped".'.format(fan_num, fan_presence)
            # Check FAN SN and PID
            found = False
            for item in userdict['genealogy']:
                if fan_sernum == item['serial_number'] and '{}='.format(fan_pid) == item['product_id']:
                    found = True
                    log.info('         + FAN SN [{}] and PID [{}]'
                             ' found in genealogy record.'.format(item['serial_number'], item['product_id']))
                    break
            if not found:
                return lib.FAIL, 'FAN PID [{}] with ' \
                                 'SN [{}] not found in genealogy record.'.format(fan_pid, fan_sernum)
            # Check FAN PN
            # test_record = get_legacy_tst_record(serial_number=fan_sernum, areas=['SYSASSY'], test_status='P')
            # if fan_pn == test_record['tan']:
            #    log.info('         + FAN PN [{}] found in tst_record.'.format(test_record['tan']))
            # else:
            #     return lib.FAIL, 'FAN PN [{}] not found in tst_record.'.format(fan_pn)

            # Check FAN VID
            # if fan_vid == test_record['hwrev']:
            #     log.info('         + FAN VID [{}] found in tst_record.'.format(test_record['hwrev']))
            # else:
            #     return lib.FAIL, 'FAN VID [{}] not found in tst_record.'.format(fan_vid)

            # Add FAN PID to userdict['found_hw']
            add_to_found_hw(fan_pid, 1)
            log.info('')
        fan_num += 1

    return lib.PASS


def check_server_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)

        conn.send(text='\r', expectphrase=['-A#', 'server #'])

        if 'server #' == conn.foundphrase:
            conn.send(text='show detail\r', expectphrase='server #')
            server_sernum = re.findall('Serial \(SN\): ?(.*)\r', conn.recbuf)[0]
            server_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
            server_pn = re.findall('Part Number: ?(.*)\r', conn.recbuf)[0]
            server_vid = re.findall('VID: ?(.*)\r', conn.recbuf)[0]

            log.info('   - Server : [{}]'.format(server_num))
            log.info('      Serial Number : [{}]'.format(server_sernum))
            log.info('      Part Number   : [{}]'.format(server_pn))
            log.info('      PID           : [{}]'.format(server_pid))
            log.info('      VID           : [{}]'.format(server_vid))

            # Check Server SN and PID
            found = False
            for item in userdict['genealogy']:
                if server_sernum == item['serial_number'] and '{}='.format(server_pid) == item['product_id']:
                    found = True
                    log.info('         + Server SN [{}] and PID [{}]'
                             ' found in genealogy record.'.format(item['serial_number'], item['product_id']))
                    break
            if not found:
                return lib.FAIL, 'Server PID [{}] with ' \
                                 'SN [{}] not found in genealogy record.'.format(server_pid, server_sernum)
            # Check Server PN
            # 73- vs 68- Matrix
            server_pn_matrix = {'73-17705-01': '68-5715-03',
                                '73-17706-01': '68-5716-01',
                                '73-18080-01': '68-6064-02',
                                '73-17425-01': '68-5650-03'}
            test_record = get_legacy_tst_record(serial_number=server_sernum, areas=['SYSASSY'], test_status='P')

            if server_pn in server_pn_matrix:
                server_pn = server_pn_matrix[server_pn]

            if server_pn == test_record['tan']:
                log.info('         + Server PN [{}] found in tst_record.'.format(test_record['tan']))
            else:
                return lib.FAIL, 'Server PN found [{}] expected [{}].'.format(server_pn, test_record['tan'])
            # Check Server VID
            if server_vid == test_record['hwrev']:
                log.info('         + Server VID [{}] found in tst_record.'.format(test_record['hwrev']))
            else:
                return lib.FAIL, 'Server VID [{}] not found in tst_record.'.format(server_vid)

            # Add Server PID to userdict['found_hw']
            add_to_found_hw(server_pid, 1)
            log.info('')
        server_num += 1

    return lib.PASS


def check_adapter_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    server_num = 1
    while server_num <= userdict['max_server_num']:
        adapter_num = 1
        while adapter_num <= userdict['max_adapter_num']:
            fxos_scope('adapter 1/{}/{}'.format(server_num, adapter_num), True)
            conn.send(text='\r', expectphrase=['-A#', 'adapter #'])

            if 'adapter #' == conn.foundphrase:
                conn.send(text='show detail\r', expectphrase='adapter #')
                adapter_sernum = re.findall('Serial: ?(.*)\r', conn.recbuf)[0]
                adapter_pid = re.findall('PID: ?(.*)\r', conn.recbuf)[0]
                conn.send(text='show ext-eth-if 1 detail\r', expectphrase='adapter #')
                adapter_mac_eth1 = re.findall('Mac: ?(.*)\r', conn.recbuf)[0]
                conn.send(text='show ext-eth-if 5 detail\r', expectphrase='adapter #')
                adapter_mac_eth5 = re.findall('Mac: ?(.*)\r', conn.recbuf)[0]
                log.info('   - Server / Adapter : [{}/{}]'.format(server_num, adapter_num))
                log.info('      Serial Number   : [{}]'.format(adapter_sernum))
                log.info('      Mac Eth 1       : [{}]'.format(adapter_mac_eth1))
                log.info('      Mac Eth 5       : [{}]'.format(adapter_mac_eth5))

                # Check Adapter SN
                found = False
                for item in userdict['genealogy']:
                    if adapter_sernum == item['serial_number']:
                        found = True
                        log.info('         + Adapter SN [{}] found in '
                                 'genealogy record.'.format(item['serial_number']))
                        break
                if not found:
                    return lib.FAIL, 'Adapter SN [{}] not found in genealogy record.'.format(adapter_sernum)
                # Check Adapter Mac Verify and Prefix verify
                cesiumlib.verify_mac(serial_number=adapter_sernum,
                                     uut_type=adapter_pid,
                                     mac_start_address='{}'.format(''.join(re.findall(r'\w', adapter_mac_eth1))),
                                     block_size=12)
                log.info('         + Mac Verify Eth1 [{}] OK!'.format(adapter_mac_eth1))
                if adapter_mac_eth1[:9] == adapter_mac_eth5[:9]:
                    log.info('         + Mac Prefix [{}] Match!'.format(adapter_mac_eth1[:9]))
                else:
                    return lib.FAIL, 'Mac Prefix Mismatch Eth1 [{}] ' \
                                     'Eth5 [{}].'.format(adapter_mac_eth1[:9], adapter_mac_eth5[:9])
                log.info('')

            adapter_num += 1
        server_num += 1

    return lib.PASS


def check_hdd_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    get_genealogy_structure()
    os_login()

    if ('FPR9K-SM-24' in userdict['ordered_hw'] or
            'FPR9K-SM-24-NEB' in userdict['ordered_hw'] or
            'FPR9K-SM-36' in userdict['ordered_hw'] or
            'FPR9K-SM-44' in userdict['ordered_hw']):
        exp_hdd_size = 761985

    server_num = 1
    while server_num <= userdict['max_server_num']:
        hdd_num = 1
        while hdd_num <= userdict['max_hard_drive_num']:
            fxos_scope('server 1/{}'.format(server_num), True)
            conn.send(text='\r', expectphrase=['-A#', 'server #'])
            if 'server #' == conn.foundphrase:
                fxos_scope('raid-controller 1 sas', False)
                fxos_scope('local-disk {}'.format(hdd_num), False)
                conn.send(text='\r', expectphrase=['-A#', 'local-disk #'])

                if 'local-disk #' == conn.foundphrase:
                    conn.send(text='show detail\r', expectphrase='local-disk #')
                    hdd_presence = re.findall('Presence: ?(.*)\r', conn.recbuf)[0]
                    hdd_size = re.findall('Size \(MB\): ?(.*)\r', conn.recbuf)[0]
                    log.info('   - Server / HDD : [{}/{}]'.format(server_num, hdd_num))
                    log.info('      Presence    : [{}]'.format(hdd_presence))
                    log.info('      Size        : [{}]'.format(hdd_size))
                    # Check Presence
                    if hdd_presence == 'Equipped':
                        log.info('         + HDD Presence OK!')
                    else:
                        return lib.FAIL, 'Server/HDD [{}/{}] presence [{}] ' \
                                         'expected "Equipped".'.format(server_num, hdd_num, hdd_presence)
                    # Check Size
                    if int(hdd_size) == exp_hdd_size:
                        log.info('         + HDD Size [{}] OK!'.format(hdd_size))
                    else:
                        return lib.FAIL, 'Server/HDD [{}/{}] incorect size, ' \
                                         'found [{}] expected [{}].'.format(server_num, hdd_num,
                                                                            hdd_size, exp_hdd_size)
            else:
                break
            log.info('')
            hdd_num += 1
        server_num += 1

    return lib.PASS


def check_sd_card_details():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']
    exp_sd_count = 0

    get_genealogy_structure()
    os_login()

    if ('FPR9K-SM-24' in userdict['ordered_hw'] or
            'FPR9K-SM-24-NEB' in userdict['ordered_hw'] or
            'FPR9K-SM-36' in userdict['ordered_hw'] or
            'FPR9K-SM-44' in userdict['ordered_hw']):
        exp_sd_count = 0

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)
        conn.send(text='\r', expectphrase=['-A#', 'server #'])
        if 'server #' == conn.foundphrase:
            fxos_scope('flexflash-controller 1', False)
            conn.send(text='\r', expectphrase=['-A#', 'flexflash-controller #'])

            if 'flexflash-controller #' == conn.foundphrase:
                conn.send(text='show detail\r', expectphrase='flexflash-controller #')
                flexflash_count = re.findall('Physical Drive Count: ?(.*)\r', conn.recbuf)[0]
                log.info('   - Server/Flexflash : [{}/1]'.format(server_num))
                log.info('      SD Count : [{}]'.format(flexflash_count))

                if int(flexflash_count) == exp_sd_count:
                    log.info('         + SD Count OK!')
                else:
                    return lib.FAIL, 'SD Count mismatch! Found [{}] Expected [{}].'.format(flexflash_count,
                                                                                           exp_sd_count)
                log.info('')
        server_num += 1

    return lib.PASS


def check_configuration():

    userdict = lib.apdicts.userdict

    chk = True
    log.info('   {:<20} {:<7} {:<7} {:<8}'.format('PID', 'UUT', 'ORDER', 'Result'))
    log.info('   -------------------- ------- ------- --------')

    pids = filter(None, list(set(list(userdict['ordered_hw'].keys()) + list(userdict['found_hw'].keys()))))
    for pid in pids:
        result = 'OK'
        if userdict['ordered_hw'].get(pid, 0) != userdict['found_hw'].get(pid, 0):
            result = 'ERROR'
            chk = False
        log.info('   {:<20} {:<7} {:<7} {:<8}'.format(pid, '[{}]'.format(userdict['found_hw'].get(pid, 0)),
                                                      '[{}]'.format(userdict['ordered_hw'].get(pid, 0)), result))
    log.info('')

    if not chk:
        return lib.FAIL, "Configuration Mismatch, please check!"

    return lib.PASS


def check_system_health():
    """Check System Health

    This routine will check system health.
    """

    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    os_login()

    conn.send(text='terminal length 0\r', expectphrase='-A#', timeout=10)
    # System Health Information
    log.info('   - Checking System Health Information ...')
    conn.send(text='show chassis inventory expand detail\r', expectphrase='-A#')
    if 'Error' in conn.recbuf or 'Unknown' in conn.recbuf:
        log.info('      FAIL!')
        return lib.FAIL, "'Error' or 'Unknown' found in command output. Please check!"

    conn.send(text='connect fxos\r', expectphrase='(fxos)#')
    conn.send(text='show module\r', expectphrase='(fxos)#')
    if 'Failed' in conn.recbuf or 'Down' in conn.recbuf:
        log.info('      FAIL!')
        return lib.FAIL, "'Failed' or 'Down' found in command output. Please check!"

    conn.send(text='exit\r', expectphrase='-A#')
    log.info('      OK!')
    # Card Detail
    log.info('   - Checking Card Detail ...')
    fxos_scope('fabric-interconnect a', True)
    conn.send(text='show card detail\r', expectphrase='interconnect #')
    if 'Operable' not in conn.recbuf:
        log.info('      FAIL!')
        return lib.FAIL, "'Operable' status not found. Please check!"
    conn.send(text='exit\r', expectphrase='-A#')
    log.info('      OK!')
    # Tech Support Information
    """
    log.info('   - Display Tech Support Information ...')
    conn.send(text='connect local-mgmt\r', expectphrase='(local-mgmt)#')
    conn.send(text='show tech-support fprm brief\r', expectphrase='(local-mgmt)#', timeout=120)
    conn.send(text='exit\r', expectphrase='-A#')
    log.info('      OK!')
    """
    # Syslogs (default level) Information
    log.info('   - Display Syslogs Information ...')
    conn.send(text='connect fxos\r', expectphrase='(fxos)#')
    conn.send(text='show logging logfile\r', expectphrase='(fxos)#')
    conn.send(text='exit\r', expectphrase='-A#')
    log.info('      OK!')
    # DIMM Sensor Status
    mem_location = {'FPR9K-SM-36': ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2',
                                    'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2'],
                    'FPR9K-SM-44': ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'],
                    'FPR9K-SM-24': ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2',
                                    'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2'],
                    'FPR-4110-K9': ['A1', 'B1', 'C1', 'D1'],
                    'FPR-4120-K9': ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1'],
                    'FPR-4140-K9': ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'D1', 'D2',
                                    'E1', 'E2', 'F1', 'F2', 'G1', 'G2', 'H1', 'H2'],
                    'FPR-4150-K9': ['A1', 'B1', 'C1', 'D1', 'E1', 'F1', 'G1', 'H1']}

    log.info('   - Checking DIMM Sensor Status ...')
    for item in userdict['ordered_hw']:
        if item in mem_location.keys():
            server_num = 1
            while server_num <= userdict['max_server_num']:
                conn.send(text='connect cimc 1/{}\r'.format(server_num), expectphrase=['-A#', '[ help ]#'])
                if conn.foundphrase == '[ help ]#':
                    conn.send(text='sensors\r', expectphrase='[ sensors ]#', timeout=30)
                    # CHECKING HERE
                    mem_loc_found = []
                    for line in conn.recbuf.splitlines()[1:]:
                        line_strip = list(map(str.strip, line.split("|")))
                        if '_ECC' in line_strip[0] and line_strip[2] == 'error' and line_strip[3] == 'OK':
                            mem_loc_found.extend([line_strip[0][8:10]])

                    conn.send(text='exit\r', expectphrase='-A#')
                    log.info('      - Checking Memory Location for [{}] on Server [{}] ...'.format(item, server_num))
                    if mem_location[item] == mem_loc_found:
                        log.info('         OK!')
                    else:
                        log.info('         FAIL!')
                        return lib.FAIL, 'Expected Locations [{}] Found [{}]'.format(mem_location[item], mem_loc_found)
                server_num += 1
    # SM Modules (server) Memory Status
    log.info('   - Checking SM Modules Memory Status ...')
    for item in userdict['ordered_hw']:
        if item in mem_location.keys():
            server_num = 1
            while server_num <= userdict['max_server_num']:
                conn.send(text='show server memory 1/{}\r'.format(server_num), expectphrase='-A#')
                if 'Server 1/{}'.format(server_num) in conn.recbuf:
                    # CHECKING HERE
                    mem_loc_found = []
                    for line in conn.recbuf.splitlines()[1:]:
                        line_strip = list(map(str.strip, line.split()))
                        if line_strip[0].isdigit() and 'Equipped' == line_strip[2] and 'Operable' == line_strip[3]:
                            mem_loc_found.extend([line_strip[1]])

                    log.info('      - Checking Memory Location for [{}] on Server [{}] ...'.format(item, server_num))
                    if mem_location[item] == mem_loc_found:
                        log.info('         OK!')
                    else:
                        log.info('         FAIL!')
                        return lib.FAIL, 'Expected Locations [{}] Found [{}]'.format(mem_location[item], mem_loc_found)
                server_num += 1

    return lib.PASS


def check_adapters_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_adapter_version']

    server_num = 1
    while server_num <= userdict['max_server_num']:
        adapter_num = 1
        while adapter_num <= userdict['max_adapter_num']:
            fxos_scope('adapter 1/{}/{}'.format(server_num, adapter_num), True)
            conn.send(text='\r', expectphrase=['-A#', 'adapter #'])

            if 'adapter #' == conn.foundphrase:
                conn.send(text='show version\r', expectphrase='adapter #')

                adapter_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
                log.info('- Server / Adapter : [{}/{}]'.format(server_num, adapter_num))
                log.info('   Running-Vers : [{}]'.format(adapter_running_ver))

                if expected_running_version == adapter_running_ver:
                    log.info('      Ok!')
                else:
                    raise Exception('Running Version Mismatch, expected [{}] '
                                    'found [{}].'.format(expected_running_version, adapter_running_ver))
                log.info('')

            adapter_num += 1
        server_num += 1

    return lib.PASS


def check_bios_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_bios_version']

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)
        conn.send(text='\r', expectphrase=['-A#', 'server #'])

        if 'server #' == conn.foundphrase:
            fxos_scope('bios', False)
            conn.send(text='show version detail\r', expectphrase='bios #')
            bios_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
            bios_startup_ver = re.findall('Startup-Vers: ?(.*)\r', conn.recbuf)[0]
            log.info('- Server [{}] ...'.format(server_num))
            log.info('   Bios Running-Vers : [{}]'.format(bios_running_ver))
            log.info('   Bios Startup-Vers : [{}]'.format(bios_startup_ver))

            if expected_running_version == bios_running_ver:
                if expected_running_version == bios_startup_ver:
                    log.info('      Ok!')
                else:
                    raise Exception('Running Version Mismatch, expected [{}] '
                                    'found [{}].'.format(expected_running_version, bios_startup_ver))
            else:
                raise Exception('Running Version Mismatch, expected [{}] '
                                'found [{}].'.format(expected_running_version, bios_running_ver))
            log.info('')

        server_num += 1

    return lib.PASS


def check_board_controller_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_board_controller_version']

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)
        conn.send(text='\r', expectphrase=['-A#', 'server #'])

        if 'server #' == conn.foundphrase:
            fxos_scope('boardcontroller', False)
            conn.send(text='show version detail\r', expectphrase='boardcontroller #')
            board_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
            board_startup_ver = re.findall('Startup-Vers: ?(.*)\r', conn.recbuf)[0]
            log.info('- Server [{}] ...'.format(server_num))
            log.info('   Board Controller Running-Vers : [{}]'.format(board_running_ver))
            log.info('   Board Controller Startup-Vers : [{}]'.format(board_startup_ver))

            if expected_running_version == board_running_ver:
                if expected_running_version == board_startup_ver:
                    log.info('      Ok!')
                else:
                    raise Exception('Running Version Mismatch, expected [{}] '
                                    'found [{}].'.format(expected_running_version, board_startup_ver))
            else:
                raise Exception('Running Version Mismatch, expected [{}] '
                                'found [{}].'.format(expected_running_version, board_running_ver))
            log.info('')

        server_num += 1

    return lib.PASS


def check_cimc_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_cimc_version']

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)
        conn.send(text='\r', expectphrase=['-A#', 'server #'])

        if 'server #' == conn.foundphrase:
            fxos_scope('cimc', False)
            conn.send(text='show version detail\r', expectphrase='cimc #')
            cimc_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
            cimc_startup_ver = re.findall('Startup-Vers: ?(.*)\r', conn.recbuf)[0]
            log.info('- Server [{}] ...'.format(server_num))
            log.info('   CIMC Running-Vers : [{}]'.format(cimc_running_ver))
            log.info('   CIMC Startup-Vers : [{}]'.format(cimc_startup_ver))

            if expected_running_version == cimc_running_ver:
                if expected_running_version == cimc_startup_ver:
                    log.info('      Ok!')
                else:
                    raise Exception('Running Version Mismatch, expected [{}] '
                                    'found [{}].'.format(expected_running_version, cimc_startup_ver))
            else:
                raise Exception('Running Version Mismatch, expected [{}] '
                                'found [{}].'.format(expected_running_version, cimc_running_ver))
            log.info('')

        server_num += 1

    return lib.PASS


def check_ssp_os_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_ssp_os_version']

    server_num = 1
    while server_num <= userdict['max_server_num']:
        fxos_scope('server 1/{}'.format(server_num), True)
        conn.send(text='\r', expectphrase=['-A#', 'server #'])

        if 'server #' == conn.foundphrase:
            fxos_scope('fxos', False)
            conn.send(text='show version detail\r', expectphrase='fxos #')
            ssp_os_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
            log.info('- Server [{}] ...'.format(server_num))
            log.info('   SSP OS Running-Vers : [{}]'.format(ssp_os_running_ver))

            if expected_running_version == ssp_os_running_ver:
                log.info('      Ok!')
            else:
                raise Exception('Running Version Mismatch, expected [{}] '
                                'found [{}].'.format(expected_running_version, ssp_os_running_ver))
            log.info('')

        server_num += 1

    return lib.PASS


def check_system_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    expected_running_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_system_version']
    expected_package_version = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_package_version']

    fxos_scope('system', True)
    conn.send(text='show version detail\r', expectphrase='system #')
    system_running_ver = re.findall('Running-Vers: ?(.*)\r', conn.recbuf)[0]
    system_startup_ver = re.findall('Startup-Vers: ?(.*)\r', conn.recbuf)[0]
    system_package_ver = re.findall('Package-Vers: ?(.*)\r', conn.recbuf)[0]
    log.info('- System ...')
    log.info('   Running-Vers : [{}]'.format(system_running_ver))
    log.info('   Startup-Vers : [{}]'.format(system_startup_ver))
    log.info('   Package-Vers : [{}]'.format(system_package_ver))

    if expected_running_version == system_running_ver:
        if expected_running_version == system_startup_ver:
            if expected_package_version == system_package_ver:
                log.info('      Ok!')
            else:
                raise Exception('Package Version Mismatch, expected [{}] '
                                'found [{}].'.format(expected_package_version, system_package_ver))
        else:
            raise Exception('Startup Version Mismatch, expected [{}] '
                            'found [{}].'.format(expected_running_version, system_startup_ver))
    else:
        raise Exception('Running Version Mismatch, expected [{}] '
                        'found [{}].'.format(expected_running_version, system_running_ver))
    log.info('')

    return lib.PASS


def check_fabric_interconnect_version():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    exp_run_kern_ver = userdict[userdict['ordered_sw']['fxos']['image_name']]['exp_fabric_interconnect_version']

    fxos_scope('fabric-interconnect a', True)
    conn.send(text='show version\r', expectphrase='interconnect #')

    fabric_running_kern_ver = re.findall('Running-Kern-Vers: ?(.*)\r', conn.recbuf)[0]
    fabric_running_sys_ver = re.findall('Running-Sys-Vers: ?(.*)\r', conn.recbuf)[0]
    fabric_startup_kern_ver = re.findall('Startup-Kern-Vers: ?(.*)\r', conn.recbuf)[0]
    fabric_startup_sys_ver = re.findall('Startup-Sys-Vers: ?(.*)\r', conn.recbuf)[0]

    log.info('- Fabric Interconnect ...')
    log.info('   Running-Kern-Vers : [{}]'.format(fabric_running_kern_ver))
    log.info('   Running-Sys-Vers  : [{}]'.format(fabric_running_sys_ver))
    log.info('   Startup-Kern-Vers : [{}]'.format(fabric_startup_kern_ver))
    log.info('   Startup-Sys-Vers  : [{}]'.format(fabric_startup_sys_ver))

    if exp_run_kern_ver == fabric_running_kern_ver:
        if exp_run_kern_ver == fabric_running_sys_ver:
            if exp_run_kern_ver == fabric_startup_kern_ver:
                if exp_run_kern_ver == fabric_startup_sys_ver:
                    log.info('      Ok!')
                else:
                    raise Exception('Startup System Version Mismatch, expected [{}] '
                                    'found [{}].'.format(exp_run_kern_ver, fabric_startup_sys_ver))
            else:
                raise Exception('Startup Kernel Version Mismatch, expected [{}] '
                                'found [{}].'.format(exp_run_kern_ver, fabric_startup_kern_ver))
        else:
            raise Exception('Running System Version Mismatch, expected [{}] '
                            'found [{}].'.format(exp_run_kern_ver, fabric_running_sys_ver))
    else:
        raise Exception('Running Kernel Version Mismatch, expected [{}] '
                        'found [{}].'.format(exp_run_kern_ver, fabric_running_kern_ver))
    log.info('')

    return lib.PASS


def check_server_version():
    """Check Version

    This routine will check versions.
    """
    os_login()
    discover_servers()
    check_servers_operational_state()
    log.info('')
    check_adapters_version()
    check_bios_version()
    check_board_controller_version()
    check_cimc_version()
    check_ssp_os_version()
    check_system_version()
    check_fabric_interconnect_version()

    return lib.PASS


def clean_images():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    os_login()
    fxos_scope('firmware', True)

    conn.send('show package\r', expectphrase='firmware #', timeout=10)
    found_images = re.findall('(fxos-[^\s]+)', conn.recbuf)

    log.info('   - Images Found : {}'.format(found_images))
    # Delete Images
    for image in found_images:
        if image == userdict['ordered_sw']['fxos']['image_name']:
            log.info('      - Skipping [{}], this is the ordered image.'.format(image))
            continue
        log.info('      - Deleting [{}] ...'.format(image))
        conn.send(text='delete package {}\r'.format(image), expectphrase='firmware #')
        conn.send(text='show package\r', expectphrase='firmware #')
        if image in conn.recbuf:
            return lib.FAIL, "Image [{}] couldn't be erased. Please check.".format(image)
        else:
            log.info('         Ok!')
    log.info('')

    # Get CSP Applications Installed
    fxos_scope('ssa', True)
    conn.send(text='show app\r', expectphrase='ssa #')

    csp_apps_vers = []
    for line in filter(None, conn.recbuf.splitlines())[1:-1]:
        line = line.strip()
        if 'asa' in line or 'ftd' in line:
            csp_apps_vers.extend(['{}|{}'.format(line.split()[0], line.split()[1])])
    userdict['csp_apps_vers'] = csp_apps_vers
    log.info('   - CSA Apps found : {}'.format(csp_apps_vers))
    # Create csp_apps_vers_ordered from userdict[sw_ordered][csp_apps]
    csp_apps_vers_ordered = []
    for csp_app in userdict['ordered_sw']['csp_apps']:
        csp_name = re.findall('^cisco-([^\.]+)', csp_app['image_name'])[0]
        csp_version = csp_app['image_version']
        csp_apps_vers_ordered.extend(['{}|{}'.format(csp_name, csp_version)])
    csp_apps_vers_ordered = list(set(csp_apps_vers_ordered))
    # Delete CSA Apps except ordered.
    for app in csp_apps_vers:
        if app in csp_apps_vers_ordered:
            log.info('      - Skipping [{}], this CSP App is ordered.'.format(app))
            continue
        log.info('      - Deleting [{}] ...'.format(app))
        conn.send(text='delete app {} {}\r'.format(app.split("|")[0], app.split("|")[1]),
                  expectphrase='ssa\*? #', regex=True)
        conn.send(text='commit-buffer\r', expectphrase='ssa #')
        conn.send(text='show app\r', expectphrase='ssa #')
        if app.split("|")[1] in conn.recbuf:
            return lib.FAIL, "CSP App [{}] couldn't be erased. Please check.".format(app)
        else:
            log.info('         Ok!')
    log.info('')

    return lib.PASS


def download_csp_app(override=False):
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    os_login()

    for csp_app in userdict['ordered_sw']['csp_apps']:
        retry = 0
        while True:
            fxos_scope('ssa', True)
            fxos_scope('app-software', False)
            log.info('   - CSP App : [{}]'.format(csp_app['image_name']))

            if any(csp_app['image_version'] in s for s in userdict['csp_apps_vers']) and not override:
                log.info('      - CSP App already installed.')
                break

            conn.send(text='download image tftp://{}/{}\r'.format(userdict['server_ip'], csp_app['image_name']),
                      expectphrase='software #')

            if 'Incomplete Command' in conn.recbuf or \
                    'Invalid Command' in conn.recbuf or \
                    'Invalid Value' in conn.recbuf:
                if retry <= 3:
                    retry += 1
                    continue
                else:
                    return lib.FAIL, "Couldn't start image [{}] download. Please check.".format(csp_app['image_name'])
            else:
                break

        timeout = time.time() + 120
        while True:
            if any(csp_app['image_version'] in s for s in userdict['csp_apps_vers']) and not override:
                break
            fxos_scope('download-task {}'.format(csp_app['image_name']), False)
            conn.send(text='show detail\r', expectphrase='task #')
            state = re.findall('State: ?(.*)\r', conn.recbuf)[0]

            if state == 'Downloading':
                if time.time() > timeout:
                    return lib.FAIL, "Download timeout reached! Please check."
                else:
                    log.info('      - Downloading ... Wait 20 secs ...')
                    time.sleep(20)
                    conn.send(text='exit\r')
                    continue
            elif state == 'Failed':
                return lib.FAIL, "Download Failed! Please check."
            elif state == 'Downloaded':
                log.info('      - Download Completed!')
                log.info('')
                break

    return lib.PASS


def set_default_configs():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']

    while True:
        conn.send(text='end\r', expectphrase='-A#', timeout=10)
        conn.send(text='connect local-mgmt\r', expectphrase='(local-mgmt)#')
        log.info('   - Erasing Configuration ...')
        conn.send(text='erase configuration\r', expectphrase='Are you sure? (yes/no)')
        conn.send(text='yes\r', expectphrase=['-A#', 'Rommon image verified successfully'], timeout=1200)

        if 'This command can be executed only on local Fabric interconnect and by admin user only' in conn.recbuf:
            conn.send(text='exit\r', expectphrase='login:')
            os_login()
            continue
        else:
            break
    boot_rommon()

    rommon_vars = ['ADDRESS', 'NETMASK', 'GATEWAY', 'SERVER', 'TFTP_MACADDR', 'IMAGE']
    for var in rommon_vars:
        conn.send(text='unset {}\r'.format(var), expectphrase='rommon [0-9]+ >', regex=True)
    conn.send(text='sync\r', expectphrase='rommon [0-9]+ >', regex=True, timeout=10)
    conn.send(text='set\r', expectphrase='rommon [0-9]+ >', regex=True)

    for var in rommon_vars:
        try:
            val = re.findall('{}=(.*)'.format(var), conn.recbuf)[0]
        except IndexError:
            val = ''

        if val:
            return lib.FAIL, '{}={} was not cleared from rommon!'.format(var, val)

    conn.send(text='reboot\r', expectphrase='Continue? (y/n)', timeout=600)
    return lib.PASS


##################
# Debug Stuff #
##################


def verify_cmpd():
    """Verify CMPD

    As TDE, will use verify_cmpd() to check uut SPROM fields against cmpd entry
    """
    sprom = {
        'Format Version Number Common Header': '1',
        'Internal Use Area Offset': '0',
        'Chassis Info Area Offset': '1',
        'Board Area Offset': '7',
        'Product Info Area Offset': '0',
        'MultiRecord Area Offset': '0',
        'Common Header Check Sum': '247',
        'Chassis Info Area Format Version': '1',
        'Chassis Info Area Length': '6',
        'CARD_TYPE': '18',
        'Chassis Part Number Type/Length': '204',
        'TAN PART NUM': 'SKIP SPROM CHECK',
        'Chassis SN Type/Length': '203',
        'SERIAL NUMBER': 'SKIP SPROM CHECK',
        'Manufacturer Type/Length': '209',
        'MFG INFO': 'Cisco Systems Inc',
        'End of Field Marker': '193',
        'Internal Use Area Checksum': 'SKIP SPROM CHECK',
        'Board Info Area Format Version': '1',
        'Board Area Length': '12',
        'Language code': '0',
        'MFG DATE': 'SKIP SPROM CHECK',
        'Board Manufacturer Type/Length': '209',
        'MFG INFO': 'Cisco Systems Inc',
        'Board Name Type/Length': '210',
        'PRODUCT NAME /PID': 'SKIP SPROM CHECK',
        'Board Serial No. Type/Length': '203',
        'SERIAL NUMBER': 'SKIP SPROM CHECK',
        'Board Part No. Type/Length': '203',
        'PCA NUM': '73-16585-03',
        'FRU File ID Type/Length': '196',
        'FRU File ID': 'SKIP SPROM CHECK',
        'BOM/HW/PID length': '198',
        'PCA REVISION': 'A0',
        'PCBFAB VERSION': '3',
        'VERSION ID': 'SKIP SPROM CHECK',
        'CLEI Length': '206',
        'CLEI Code': 'SKIP SPROM CHECK',
        'End of Field Marker': '193',
        'Board Info Area Checksum': 'SKIP SPROM CHECK',
    }
    log.info(sprom)
    sprom_types = [
        'Format Version Number Common Header',
        'Internal Use Area Offset',
        'Chassis Info Area Offset',
        'Board Area Offset',
        'Product Info Area Offset',
        'MultiRecord Area Offset',
        'Common Header Check Sum',
        'Chassis Info Area Format Version',
        'Chassis Info Area Length',
        'CARD_TYPE',
        'Chassis Part Number Type/Length',
        'TAN PART NUM',
        'Chassis SN Type/Length',
        'SERIAL NUMBER',
        'Manufacturer Type/Length',
        'MFG INFO',
        'End of Field Marker',
        'Internal Use Area Checksum',
        'Board Info Area Format Version',
        'Board Area Length',
        'Language code',
        'MFG DATE',
        'Board Manufacturer Type/Length',
        'MFG INFO',
        'Board Name Type/Length',
        'PRODUCT NAME /PID',
        'Board Serial No. Type/Length',
        'SERIAL NUMBER',
        'Board Part No. Type/Length',
        'PCA NUM',
        'FRU File ID Type/Length',
        'FRU File ID',
        'BOM/HW/PID length',
        'PCA REVISION',
        'PCBFAB VERSION',
        'VERSION ID',
        'CLEI Length',
        'CLEI Code',
        'End of Field Marker',
        'Board Info Area Checksum',
    ]
    log.info(sprom_types)
    sprom_values = [
        '1',
        '0',
        '1',
        '7',
        '0',
        '0',  # should be 0
        '247',
        '1',
        '6',
        '18',
        '204',
        '68-100280-03',
        '203',
        'SKIP SPROM CHECK',
        '209',
        'Cisco Systems Inc',
        '193',
        '7B',
        '1',
        '12',
        '0',
        'SKIP SPROM CHECK',
        '209',
        'Cisco Systems Inc',
        '210',
        'FPR-C9300-AC',
        '203',
        'SKIP SPROM CHECK',
        '203',
        '73-16585-03',
        '196',
        '0-AC',
        '198',
        'A0',
        '3',
        'V01',
        '206',
        'FWMAM00BRA',
        '193',
        'SKIP SPROM CHECK',
    ]
    cesiumlib.verify_cmpd(
        'SPROM',
        'FPR-C9300-AC',
        '73-16585-03',
        'A0',
        'ALL',
        sprom_values,
        'SSP',
        skip_value='SKIP SPROM CHECK',
    )
    return lib.PASS


def copy_file_to_uut(files, location, c, product):
    """ This function will copy files to UUT from AP machine tftpboot.

    :return: lib.PASS
    """

    userdict = lib.apdicts.userdict
    con = c

    for f in files:
        if product == 'BS.diag':
            dir_txt = 'dir /{}\r'.format(location)
            copy_txt = 'scp gen-apollo@{}:/tftpboot/{} /{}\r'.format(
                userdict['server_ip'],
                f, location)
        elif product in ['BS.kick']:
            dir_txt = 'dir {}\r'.format(location)
            copy_txt = 'copy scp://{}/tftpboot/{} {}\r'.format(
                userdict['server_ip'], f, location)

        con.send(text='term len 0\r', expectphrase=['>', '#'])
        con.send(text=dir_txt, expectphrase=['switch\(boot\)\#',
                                             'switch#'], regex=True, timeout=10)
        if f in con.recbuf:
            log.info("   File '{}' already copied!".format(f))
            continue
        else:
            log.info('   Copying : {}'.format(f))
            con.send(text=copy_txt)

            retry = 0
            while True:
                con.waitfor(expectphrase=['switch\(boot\)\#',
                                          'switch#',
                                          'Enter username:',
                                          'password:',
                                          'continue connecting \(yes/no\)\?',
                                          "Enter vrf \(If no input, current vrf 'default' is considered\):",
                                          'No such file or directory'], regex=True, timeout=90)
                if re.compile('switch\(boot\)\#|switch#').match(con.foundphrase):
                    con.send(text=dir_txt, expectphrase=['switch\(boot\)\#',
                                                         'switch#'], regex=True, timeout=10)
                    if f in con.recbuf:
                        log.info('     Done!')
                        break
                    else:
                        if retry <= 10:
                            retry += 1
                            log.info('    Retrying ...')
                            con.send(text=copy_txt)
                            continue
                        else:
                            raise Exception('Max number of retries reached!')
                elif 'Enter username:' in con.foundphrase:
                    con.send(text='gen-apollo\r')
                elif 'password:' in con.foundphrase:
                    con.send(text='Ad@pCr01!\r')
                elif 'continue connecting (yes/no)?' in con.foundphrase:
                    con.send(text='yes\r')
                elif "Enter vrf (If no input, current vrf 'default' is considered):" in con.foundphrase:
                    con.send(text='management\r')
                elif 'No such file or directory' in con.foundphrase:
                    raise Exception('File [{}] not in tftpboot!'.format(f))
                else:
                    raise Exception('Something went wrong!')


def get_legacy_tst_record(serial_number, areas, test_status):
    data_array = cesiumlib.get_legacy_tst(serial_number=serial_number, areas=areas)

    record_time = '1900-01-01 00:00:00'
    tst_record = {}
    for key in data_array:
        if key['result_pass_fail'] == test_status and key['test_record_time'] > record_time:
            record_time = key['test_record_time']
            tst_record = key

    return tst_record


def get_genealogy_structure(force=False):
    userdict = lib.apdicts.userdict

    if 'genealogy' not in userdict.keys() or force:
        userdict['genealogy'] = cesiumlib.get_genealogy(serial_number=userdict['sn'],
                                                        product_id=userdict['pid'],
                                                        level=10)['genealogy_structure']


def os_login():
    userdict = lib.apdicts.userdict
    conn = userdict['conn']
    conn.send(text='\r', expectphrase=['#', 'login:'])
    if 'login:' == conn.foundphrase:
        conn.send(text='admin\r', expectphrase='assword:')
        conn.send(text='cisco123\r', expectphrase='-A#')
    elif '#' == conn.foundphrase:
        conn.send(text='end\r', expectphrase='-A#')


def add_to_found_hw(pid, qty):
    userdict = lib.apdicts.userdict
    if 'found_hw' not in userdict.keys():
        userdict['found_hw'] = {}

    if pid in userdict['found_hw']:
        userdict['found_hw'][pid] += qty
    else:
        userdict['found_hw'][pid] = qty


def add_debug_patches():
    '''Add Debug Patches to Testing

    Gives ability to have seperated debug patches that will never been within
    production testing. Only Debug testing
    '''
    userdict = lib.apdicts.userdict
    # Ensure Apollo Mode is Debug
    if not lib.get_apollo_mode() == 'DEBUG':
        return lib.FAIL

    # Copy Debug Patches over for use
    for path in userdict['debug_patches']:
        userdict['patches'][path] = userdict['debug_patches'][path]

    return lib.PASS


SERIAL_NUMBER = 'serial_number'
UUT_TYPE = 'uut_type'
PREV_AREA = 'prev_area'


def debug_areacheck():
    udict = lib.apdicts.userdict
    try:
        cesiumlib.verify_area(serial_number=udict[SERIAL_NUMBER],
                              uut_type=udict[UUT_TYPE],
                              area=udict[PREV_AREA])
    except lib.apexceptions.ServiceFailure:
        return lib.FAIL
    return lib.PASS