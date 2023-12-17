"""
This utility will take the JSON format and convert/encode to binary format.
"""
import json
import typing
from collections import OrderedDict


def pcamap_schema_import(filename: str) -> typing.OrderedDict:
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
        pcamap[field_name] = {'start_addr': start_addr, 'type': field_type, 'length': field_length, 'value': ''}

    return pcamap


class TraceData:
    """
    This class will take the trace data input from JSON file and add it ot the PCAMAP OrderedDict
    """
    def __init__(self, pcamap: typing.OrderedDict, json_filename: str):
        self.pcamap = pcamap
        self.json_filename = json_filename
        self.json_data = self.get_trace_value_from_json()

    def get_trace_value_from_json(self):
        """
        Load the json object into a file
        """
        with open(self.json_filename, 'r') as jf:
            json_data = json.load(jf)
        return json_data


if __name__ == '__main__':
    eeprom_schema_file = 'eeprom_format_doc.txt'
    json_value_file = 'data_sample.json'
    pcamap = pcamap_schema_import(eeprom_schema_file)

    trace = TraceData(pcamap, json_value_file)
    d = trace.get_trace_value_from_json()
    print(d)
