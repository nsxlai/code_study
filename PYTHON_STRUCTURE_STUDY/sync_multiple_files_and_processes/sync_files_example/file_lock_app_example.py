"""
source: https://www.youtube.com/watch?v=YlUkwspocMI
source: https://py-filelock.readthedocs.io/en/latest/index.html

Before running the main function, reset the "counter.txt" counter to 0 or any other desired starting value

This example will use the filelock Python package (not included in the standard library)

At the command prompt, use the bash script to run multiple instance of this Python script
for i in {1..3}; do python file_lock_app_example.py & done
"""
import filelock
import time


file_path = 'counter.txt'
lock_path = 'counter.txt.lock'  # create the filelock object; it is different from the actual file to be locked
lock = filelock.FileLock(lock_path, timeout=1)


for _ in range(50):
    with lock:
        with open(file_path, 'r') as f:
            current = int(f.read())
            # print(f'{current = }')

        current += 1

        with open(file_path, 'w') as f:
            f.write(str(current))
        time.sleep(0.1)
