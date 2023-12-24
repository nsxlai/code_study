"""
This utility will take the JSON format and convert/encode to binary format.

To check the EEPROM values:
(base) deepspace9@Rays-Mac-mini project_EEPROM % python -m hexdump eeprom_binary.bin
00000000: FF FF FF 01 FE FF FF FF  FF FF FF FF FF FF FF FF  ................
00000010: 31 31 32 33 33 34 34 53  50 32 45 30 31 33 34 35  1123344SP2E01345
00000020: 37 30 31 33 32 33 30 34  35 36 41 42 FF FF FF FF  7013230456AB....
00000030: 33 32 34 30 34 30 30 30  30 30 30 30 30 5A FF FF  3240400000000Z..
00000040: 04 29 87 34 53 FF FF FF  FF FF FF FF FF FF FF FF  .).4S...........
00000050: 02 02 45 67 FF FF FF FF  FF FF FF FF FF 44 56 FF  ..Eg.........DV.
00000060: 50 33 32 34 35 31 39 FF  43 44 46 39 33 34 33 FF  P324519.CDF9343.
00000070: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
00000080: 32 30 32 33 31 32 31 34  31 35 3A 33 34 3A 33 35  2023121415:34:35
00000090: DE AD BE EF CA FD FF FF  FF FF FF FF FF FF AB CD  ................
000000A0: 63 61 6C 69 66 6F 72 6E  69 61 FF FF FF FF FF FF  california......
000000B0: 32 30 32 33 31 32 31 30  30 39 3A 30 33 3A 32 33  2023121009:03:23
000000C0: 02 03 05 34 04 09 10 48  07 83 09 02 03 01 04 93  ...4...H........
000000D0: 12 04 15 03 05 40 02 09  FF FF FF FF FF FF DE CA  .....@..........

"""
import json
from collections import OrderedDict


def pcamap_schema_import(filename: str) -> OrderedDict:
    with open(filename, 'r') as f:
        fout = f.readlines()

    # Create a OrderedDict:
    pcamap = OrderedDict()
    for element in fout[1:]:
        if 'reserved' in element:  # skip over the reserved fields
            continue
        temp_list = element[:-1].split()  # remove the '\n' before splitting the string
        start_addr = temp_list[0]
        field_name = temp_list[1]
        field_type = temp_list[2]
        field_length = temp_list[3]
        pcamap[field_name] = {'start_addr': start_addr,
                              'type': field_type,
                              'length': field_length,
                              'value': ''}

    return pcamap


class TraceData:
    """
    This class will take the trace data input from JSON file and add it ot the PCAMAP OrderedDict
    """
    def __init__(self, pcamap: OrderedDict, json_filename: str):
        self.pcamap = pcamap
        self.json_filename = json_filename
        self.json_data = self.get_trace_value_from_json()
        self.populate_pcamap_values_from_json_data()

    def get_trace_value_from_json(self) -> dict:
        """
        Load the json object into a file
        """
        with open(self.json_filename, 'r') as jf:
            json_data = json.load(jf)
        return json_data

    def populate_pcamap_values_from_json_data(self):
        """
        Use the __getattribute__ to call the function name that assign the JSON values to the PCAMAP OrderedDict
        """
        for key, val in self.pcamap.items():
            if 'data' not in key:  # Will use get_data to handle calibration data collection
                self.__getattribute__(f'get_{key}')()

        # Calibration data collection
        self.get_data()

    def get_version(self):
       pcamap['version']['value'] = hex(self.json_data['manufacturing']['version'])

    def get_not_version(self):
        pcamap['not_version']['value'] = hex(0xff - self.json_data['manufacturing']['version'])

    def get_main_sn(self):
        pcamap['main_sn']['value'] = self.json_data['traceability']['main_sn']

    def get_main_pn(self):
        pcamap['main_pn']['value'] = self.json_data['traceability']['main_pn']

    def get_dls(self):
        pcamap['dls']['value'] = self.json_data['manufacturing']['dls']

    def get_pls(self):
        pcamap['pls']['value'] = self.json_data['manufacturing']['pls']

    def get_vpps(self):
        pcamap['vpps']['value'] = self.json_data['traceability']['vpps']

    def get_duns(self):
        pcamap['duns']['value'] = self.json_data['traceability']['duns']

    def get_tla_pn(self):
        pcamap['tla_pn']['value'] = self.json_data['traceability']['tla_pn']

    def get_build(self):
        pcamap['build']['value'] = self.json_data['manufacturing']['build']

    def get_pcba_sn(self):
        pcamap['pcba_sn']['value'] = self.json_data['manufacturing']['pcba_sn']

    def get_pcba_pn(self):
        pcamap['pcba_pn']['value'] = self.json_data['manufacturing']['pcba_pn']

    def get_eco(self):
        pcamap['eco']['value'] = self.json_data['manufacturing']['eco']

    def get_deviation(self):
        pcamap['deviation']['value'] = self.json_data['manufacturing']['deviation']

    def get_mfg_date(self):
        temp = self.json_data['manufacturing']['date']  # Remove ":" from the date (e.g., 10/23/2023 -> 20231023)
        temp = temp.split('/')
        temp = [temp[-1], *temp[:-1]]
        pcamap['mfg_date']['value'] = ''.join(temp)

    def get_mfg_time(self):
        pcamap['mfg_time']['value'] = self.json_data['manufacturing']['time']

    def get_mac_address(self):
        temp = self.json_data['manufacturing']['mac_address']
        temp = temp.split(':')
        temp = '0x' + ''.join(temp)
        pcamap['mac_address']['value'] = temp

    def get_crc_01(self):
        pcamap['crc_01']['value'] = '0xabcd'  # TODO will add the actual CRC-16 algorithm support function

    def get_location(self):
        pcamap['location']['value'] = self.json_data['calibration']['location']

    def get_cal_date(self):
        temp = self.json_data['calibration']['date']  # Remove ":" from the date (e.g., 10/23/2023 -> 20231023)
        temp = temp.split('/')
        temp = [temp[-1], *temp[:-1]]
        pcamap['cal_date']['value'] = ''.join(temp)

    def get_cal_time(self):
        pcamap['cal_time']['value'] = self.json_data['calibration']['time']

    def get_data(self):
        data_points = 12  # specify how many data points are there in JSON file and EEPROM schema (should be matching)
        json_data_list = self.json_data['calibration']['data']  # fetch the data from the list
        for i in range(data_points):
            data_point_name = f'data_{str(i).zfill(2)}'  # e.g., data_01
            pcamap[data_point_name]['value'] = json_data_list[i]

    def get_crc_02(self):
        pcamap['crc_02']['value'] = '0xdeca'  # TODO will add the actual CRC-16 algorithm support function


class BinaryEncode:
    """
    This class will take the pcamap OrderedDict object (udpated with values) and translate into binary string and
    encode it to a binary file
    """
    def __init__(self, pcamap: OrderedDict):
        self.pcamap = pcamap
        self.bin_val_list = []

    def _prepare_data_value(self, data: dict) -> list:
        """
        There are 3 types of data_value: hex, int, and ascii.
        Will format the data_value depends on the data_type
        """
        data_value = data['value']  # string; for hex will remove the '0x'
        data_type = data['type']  # string; int/hex/ascii
        data_length = int(data['length'])  # decimal
        start_addr = data['start_addr']
        data_output_list = []

        if data_type == 'hex':
            digit = data_length * 2  # 1 byte is has 2 digits
            data_value = data_value[2:].zfill(digit)  # remove the '0x' hex header

            if digit < len(data_value):
                """ if JSON data capture is more than EEPROM schema specified length, raise exception """
                raise ValueError(f'Start address {start_addr} EEPROM length is correct. Please check input')

            for key, val in enumerate(data_value[::2]):  # skip over every 2 digits
                f_val = data_value[key * 2] + data_value[key * 2 + 1]  # forming the 2 byte octet
                data_output_list.append(f_val)

        elif data_type == 'int':
            digit = data_length * 2  # 1 byte is has 2 digits
            data_value = str(data_value).zfill(digit)  # no '0x' hex header to remove

            if digit < len(data_value):
                """ if JSON data capture is more than EEPROM schema specified length, raise exception """
                raise ValueError(f'Start address {start_addr} EEPROM length is correct. Please check input')

            for key, val in enumerate(data_value[::2]):  # skip over every 2 digits
                f_val = data_value[key * 2] + data_value[key * 2 + 1]  # forming the 2 byte octet
                data_output_list.append(f_val)

        elif data_type == 'ascii':
            data_output_list = [hex(ord(char))[2:] for char in data_value]
            if len(data_value) < data_length:  # Data captured from JSON is less than the EEPROM schema
                for _ in range(data_length - len(data_value)):
                    data_output_list.append('ff')  # this also account if the JSON value is not define (optional)

        return data_output_list

    def populate_binary_value(self):
        cnt = 0
        for k, v in self.pcamap.items():
            start_addr = int(v['start_addr'], 16)  # decimal
            data_length = int(v['length'])  # decimal

            while cnt < start_addr:  # Prefill the 0xff
                self.bin_val_list.append('ff')
                cnt += 1

            data_out_list = self._prepare_data_value(v)
            self.bin_val_list += data_out_list
            cnt += data_length

    def write_to_binary_file(self, bin_filename: str):
        # eeprom_binary_byte = [bytes(i, 'utf-8') for i in self.bin_val_list]
        binary_transition_list = [int(element, 16) for element in self.bin_val_list]
        binary_data = bytearray(binary_transition_list)

        with open(bin_filename, 'wb+') as f:
            f.write(binary_data)


if __name__ == '__main__':
    eeprom_schema_file = 'eeprom_format_doc.txt'
    json_value_file = 'data_sample.json'
    eeprom_binary_file = 'eeprom_binary.bin'
    pcamap = pcamap_schema_import(eeprom_schema_file)

    trace = TraceData(pcamap, json_value_file)
    d = trace.get_trace_value_from_json()
    # print(pcamap)

    b = BinaryEncode(pcamap)
    b.populate_binary_value()
    b.write_to_binary_file(eeprom_binary_file)
