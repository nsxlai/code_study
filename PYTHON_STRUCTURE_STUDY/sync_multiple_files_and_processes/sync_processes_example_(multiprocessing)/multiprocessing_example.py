"""
source: https://www.youtube.com/watch?v=8wX1uEp2Jhs

Without the multiprocess lock, the result of both increasing and decreasing is not deterministic (value changes per
each execution)
"""
import multiprocessing
import time


def increase_counter(counter, lock):
    for _ in range(20):
        with lock:
            counter.value += 10
        time.sleep(0.1)


def decrease_counter(counter, lock):
    for _ in range(20):
        with lock:
            counter.value -= 50
        time.sleep(0.3)


if __name__ == '__main__':

    counter = multiprocessing.Value('i', 0)
    lock = multiprocessing.Lock()

    increase_processes = []
    decrease_processes = []

    for _ in range(5):
        p = multiprocessing.Process(target=increase_counter, args=(counter, lock))
        p.start()
        increase_processes.append(p)

    for _ in range(5):
        p = multiprocessing.Process(target=decrease_counter, args=(counter, lock))
        p.start()
        decrease_processes.append(p)

    for p in increase_processes:
        p.join()

    for p in decrease_processes:
        p.join()

    print(f'{counter.value = }')
