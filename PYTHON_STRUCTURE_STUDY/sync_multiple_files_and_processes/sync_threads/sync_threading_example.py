"""
source: https://www.youtube.com/watch?v=MbFSuk8yyjY
"""
import threading
import time
import random


class ThreadCounter:
    def __init__(self):
        self.counter = 0
        self.lock = threading.Lock()

    def count(self, thread_no):
        while True:
            with self.lock:
                self.counter += 1
                print(f'{thread_no}: Just increase counter to {self.counter}')
                time.sleep(1)
                print(f'{thread_no}: Done some work; now value is {self.counter}')
            time.sleep(random.randint(1, 3))


if __name__ == '__main__':

    tc = ThreadCounter()

    for i in range(10):
        t = threading.Thread(target=tc.count, args=(i,))
        t.start()
