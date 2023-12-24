import json
import requests
import sys
from pprint import pprint


param = {
    "SN": "45678",
    "PN": "P089-123",
    "Attributes": ["sync","exposure","F-Stop","power"],
    "Position": "front_center"
}
JSON_FILE = 'json_data.txt'


def _check_request_out(r):
    if r.status_code != 200:
        print('REST API request failed!!')
        print('-' * 20)
        pprint(r.json())
        sys.exit()
    return


def req_get():
    r = requests.get('http://localhost:8000/get_status')
    _check_request_out(r)


def _write_json_data_to_file(r):
    """
    This will take the input JSON object 'r' and save it to file
    """
    with open(JSON_FILE, 'w') as jfile:
        json_data = json.loads(r.text)
        json.dump(json_data, jfile)


def req_post():
    r = requests.post('http://localhost:8000/post_data', json=param)
    _check_request_out(r)
    _write_json_data_to_file(r)


if __name__ == '__main__':
    req_get()
    req_post()
