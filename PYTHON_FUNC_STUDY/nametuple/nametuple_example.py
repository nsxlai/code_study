# source: https://towardsdatascience.com/understand-how-to-use-namedtuple-and-dataclass-in-python-e82e535c3691
from collections import namedtuple
from typing import NamedTuple


if __name__ == '__main__':
    Transaction = namedtuple('Transaction', ['sender', 'receiver', 'date', 'amount'])
    print(dir(Transaction))
    # print(f'{Transaction() = }')  # Will get TypeError for no value to initialize each of the nametuple fields
    record = Transaction(sender='test_subject01', amount=10.0, receiver='test_subject02', date='2020-10-20')
    print(f'{record = }')
    print(f'{record.receiver = }')

    # Use _make method to create the object
    record2 = Transaction._make(['subject01', 'subject02', '2020-10-20', 15.0])
    print(f'{record2 = }')
    print(f'{record2.sender = }')

    TransactionDefault = namedtuple('Transaction', ['sender', 'receiver', 'date', 'amount'],
                                    defaults=['subject01', 'subject02', None, None])
    print(f'{TransactionDefault()}')  # Will not get the TypeError since all fields are initialized at default value

    Transaction2 = namedtuple('Transaction', ['sender', 'receiver', 'date', 'amount'], defaults=[None])
    # print(f'{Transaction2()}')  # Will get TypeError since only amount will get initialize with None.

    #--------------------------------------------------------------------------------------
    class Transaction5(NamedTuple):
        sender: str
        receiver: str
        date: str
        amount: float

    record5 = Transaction5(sender='subject05', receiver='subject06', date='2020-10-20', amount=30.0)
    print(f'{record5 = }')
    print(f'{record5.date = }')
    print(f'{record5[-1] = }')
