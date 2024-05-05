# source: https://towardsdatascience.com/understand-how-to-use-namedtuple-and-dataclass-in-python-e82e535c3691
from typing import NamedTuple
import collections
from dataclasses import dataclass
from timeit import timeit
import sys
import pandas as pd


# regular class
class TransactionObject:

    def __init__(self, sender, receiver, date, amount):
        self.sender = sender
        self.receiver = receiver
        self.date = date
        self.amount = amount


# named tuple from collections
TransactionNamedTuple = collections.namedtuple('TransactionNamedTuple', ['sender', 'receiver', 'date', 'amount'])


# named tuple from typing class
class TransactionNamedTupleTyping(NamedTuple):
    sender: str
    receiver: str
    date: str
    amount: float


# dataclass
@dataclass
class TransactionDataClass:
    sender: str
    receiver: str
    date: str
    amount: float


# dataclass with slot
@dataclass
class TransactionDataClassWithSlot:
    __slots__ = ['sender', 'amount', 'receiver', 'date']
    sender: str
    receiver: str
    date: str
    amount: float


if __name__ == '__main__':
    trans_obj = TransactionObject(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender='jojo')
    trans_obj_size = sys.getsizeof(trans_obj)
    trans_named_tuple = TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender='jojo')
    trans_named_tuple_size = sys.getsizeof(trans_named_tuple)
    trans_named_tuple_typing = TransactionNamedTupleTyping(amount=1.0, receiver="xiaoxu", date="2019-01-01",
                                                           sender='jojo')
    trans_named_tuple_typing_size = sys.getsizeof(trans_named_tuple_typing)
    trans_dataclass = TransactionDataClass(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender='jojo')
    trans_dataclass_size = sys.getsizeof(trans_dataclass)
    trans_dataclass_slot = TransactionDataClassWithSlot(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender='jojo')
    trans_dataclass_slot_size = sys.getsizeof(trans_dataclass_slot)
    col_size = [trans_obj_size, trans_named_tuple_size, trans_named_tuple_typing_size,
                trans_dataclass_size, trans_dataclass_slot_size]

    # Creating the object
    create_obj = timeit('TransactionObject(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                        globals=globals())
    create_named_tuple = timeit(
        'TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")', globals=globals())
    create_named_tuple_typing = timeit(
        'TransactionNamedTupleTyping(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
        globals=globals())
    create_dataclass = timeit('TransactionDataClass(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                              globals=globals())
    create_dataclass_slot = timeit(
        'TransactionDataClassWithSlot(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
        globals=globals())
    col_create_time = [create_obj, create_named_tuple, create_named_tuple_typing,
                       create_dataclass, create_dataclass_slot]

    # Access the object
    get_obj = timeit('tans_obj.receiver',
                     setup='tans_obj = TransactionObject(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                     globals=globals())
    get_named_tuple = timeit('trans_named_tuple.receiver',
                             setup='trans_named_tuple = TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                             globals=globals())
    get_named_tuple_typing = timeit('trans_named_tuple_typing.receiver',
                                    setup='trans_named_tuple_typing = TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                                    globals=globals())
    get_dataclass = timeit('trans_dataclass.receiver',
                           setup='trans_dataclass = TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                           globals=globals())
    get_dataclass_slot = timeit('trans_dataclass_slot.receiver',
                                setup='trans_dataclass_slot = TransactionNamedTuple(amount=1.0, receiver="xiaoxu", date="2019-01-01", sender="jojo")',
                                globals=globals())
    col_access_time = [get_obj, get_named_tuple, get_named_tuple_typing, get_dataclass, get_dataclass_slot]

    obj_data = pd.DataFrame([col_size, col_create_time, col_access_time], columns=['Obj Size', 'Obj Create Time', 'Obj Access Time'])
    print(obj_data)
