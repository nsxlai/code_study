import os
from pprint import pprint

if __name__ == '__main__':
    pprint(f'{os.environ = }')
    print(f'{os.environ.get("USERNAME")}')
    print('Add environmental variable: FAKE_PASSWORD')
    os.environ.setdefault('FAKE_PASSWORD', 'TEST001')
    print(f'{os.environ.get("FAKE_PASSWORD")}')
