#!/usr/bin/env python
from tqdm import tqdm
from progress.bar import Bar
from time import sleep
from random import randint


def progress_bar() -> None:
    bar = Bar('Progress bar', max=10)
    for i in range(10):
        bar.next()
    bar.finish()


def rand_int_gen() -> int:
    return randint(0, 100)


def tqdm_bar() -> None:
    out_list = []
    for i in tqdm(range(100)):
        out_list.append(randint(0, 100))
        sleep(0.1)


if __name__ == '__main__':
    print('Traditional progress bar')
    progress_bar()

    print('Newer style progress bar')
    tqdm_bar()
