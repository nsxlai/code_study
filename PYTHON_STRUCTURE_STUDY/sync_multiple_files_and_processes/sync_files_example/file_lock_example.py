"""
source: https://www.youtube.com/watch?v=YlUkwspocMI

Before running the main function, reset the "counter.txt" counter to 0 or any other desired starting value
"""
import time
import threading


FILENAME = 'counter.txt'
LOCK = threading.Lock()  # will handle the acquire() and release() with context manager


def increase_counter(amount: int):
    for _ in range(amount):
        with LOCK:
            with open(FILENAME, 'r') as f:
                current = int(f.read())

            current += 1

            with open(FILENAME, 'w') as f:
                f.write(str(current))

            time.sleep(0.1)


if __name__ == '__main__':

    for _ in range(15):
        threading.Thread(target=increase_counter, args=(10,)).start()
