Detail: https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/

> >>>
>>> a = [2, 4, 6, 8, 10]
>>>
>>> a
[2, 4, 6, 8, 10]
>>>
>>> b = a
>>>
>>> b
[2, 4, 6, 8, 10]
>>>
>>> b.append(12)
>>> a
[2, 4, 6, 8, 10, 12]
>>> b
[2, 4, 6, 8, 10, 12]
>>>
>>>
>>> a == b
True
>>> id(a)
140430235925952
>>>
>>>
>>> id(b)
140430235925952
>>>
>>>
>>> import copy
>>> dir(copy)
['Error', '__all__', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__spec__', '_copy_dispatch', '_copy_immutable', '_deepcopy_atomic', '_deepcopy_dict', '_deepcopy_dispatch', '_deepcopy_list', '_deepcopy_method', '_deepcopy_tuple', '_keep_alive', '_reconstruct', 'copy', 'deepcopy', 'dispatch_table', 'error']
>>>
>>>
>>> c = copy.copy(a)
>>> c
[2, 4, 6, 8, 10, 12]
>>> id(c)
140430211437184
>>>
>>>
>>> c.append(14)
>>> c
[2, 4, 6, 8, 10, 12, 14]
>>> a
[2, 4, 6, 8, 10, 12]
>>> b
[2, 4, 6, 8, 10, 12]
>>>
>>>
>>> def show_list(in_lst: list) -> None:
...     print(in_lst)
...     print(id(in_lst))
...
>>>
>>> show_list(a)
[2, 4, 6, 8, 10, 12]
140430235925952
>>>
>>> show_list(c)
[2, 4, 6, 8, 10, 12, 14]
140430211437184
>>>