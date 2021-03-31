"""
source: https://medium.com/python-features/pythons-gil-a-hurdle-to-multithreaded-program-d04ad9c1a63

This article is NOT recommending using threading to do any CPU intensive task due to GIL limitation.
There is not significant benefit for doing so:

'This demonstrates the effect of the GIL on programs running in the standard CPython interpreter.
Therefore it’s not recommended to use multithreading for CPU intensive tasks in Python.'
"""
from time import time
from threading import Thread
from typing import Generator


def factorize(number: int) -> Generator:
    for i in range(1, number + 1):
        if number % i == 0:
            yield i


class FactorizeThread(Thread):
    def __init__(self, number: int):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorize(self.number))


if __name__ == '__main__':
    print(list(factorize(45)))

    numbers = [8402868, 2295738, 5938342, 7925426]
    start = time()
    for number in numbers:
        list(factorize(number))
    end = time()
    print('Took %.3f seconds' % (end - start))

    start = time()
    threads = []
    for number in numbers:
        thread = FactorizeThread(number)
        thread.start()
        threads.append(thread)
    # wait for all thread to finish
    for thread in threads:
        thread.join()
    end = time()
    print('Took %.3f seconds' % (end - start))  # It will take longer to run parallel threads than single thread.




