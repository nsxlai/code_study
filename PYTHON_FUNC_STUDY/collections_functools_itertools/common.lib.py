import collections
import itertools
import functools


if __name__ == '__main__':
    print(dir(collections))
    print('From collections library: ')
    print('Counter, OrderedDict, defaultdict, deque, namedtuple')
    print('-' * 20)
    print(dir(itertools))
    print('From itertools library: ')
    print('accumulate, chain, combinations, combinations_with_replacement, dropwhile, filterfalse, '
          'permutations, product, repeat, takewhile, zip_longest')
    print('-' * 20)
    print(dir(functools))
    print('From functools library: ')
    print('lru_cache, namedtuple, partial, reduce, wraps')
    print('-' * 20)