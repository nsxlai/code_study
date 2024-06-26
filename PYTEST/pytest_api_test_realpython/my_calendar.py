import requests
from datetime import datetime


def is_weekday():
    today = datetime.today()
    return 0 <= today.weekday() < 5


def get_holidays():
    r = requests.get('http://localhost/api/holidays')
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 404:
        return 'Page Not Found'
    return None


def set_variable():
    cert = 'dummy variable'
    return cert
