"""
For printing the json format in Linux, use jq package:
    To install: sudo apt install jq

    To display json (example):
    cat diag_report.json | jq .diag.poll_result.PMIC_BUCK1
"""
import json
from pprint import pprint


FILENAME = 'diag_report.json'


if __name__ == '__main__':
    with open(FILENAME, 'r') as f:
        f_out = f.read()

    jf = json.loads(f_out)

    pprint(jf)

    print(f'{jf["diag"] = }')
