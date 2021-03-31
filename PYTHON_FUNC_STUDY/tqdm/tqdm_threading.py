from threading import Thread
from tqdm import tqdm
from time import sleep
import os


def main_task(runtime: int) -> None:
    print('Task started')
    sleep(runtime)
    # print('Task finished!')


def tqdm_bar(runtime: int) -> None:
    for i in tqdm(range(runtime)):
        sleep(1)


if __name__ == '__main__':
    runtime = 10
    thread1_1 = Thread(target=main_task, args=(runtime, ))
    thread1_2 = Thread(target=tqdm_bar, args=(runtime, ))
    thread2_1 = Thread(target=main_task, args=(runtime,))
    thread2_2 = Thread(target=tqdm_bar, args=(runtime,))

    thread1_1.start()
    thread1_2.start()
    thread1_1.join()
    thread1_2.join()

    thread2_1.start()
    thread2_2.start()
    thread2_1.join()
    thread2_2.join()
