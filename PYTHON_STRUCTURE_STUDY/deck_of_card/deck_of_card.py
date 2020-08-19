from collections import namedtuple
from random import choice, shuffle
from itertools import product

Card = namedtuple('Card', ['rank', 'suit'])


class FrenchDeck:
    ranks = [str(n) for n in range(2, 11)] + list('JQKA')
    suits = 'spades diamonds clubs hearts'.split()

    def __init__(self):
        self._cards = [Card(rank, suit) for rank, suit in product(self.suits, self.ranks)]
        # self._cards = [Card(rank, suit) for suit in suits
        #                                 for rank in self.ranks]

    def __len__(self):
        return len(self._cards)

    def __getitem__(self, position):
        return self._cards[position]


if __name__ == '__main__':
    beer_card = Card('7', 'diamonds')
    print(f'beer_card = {beer_card}')

    deck = FrenchDeck()
    print(f'Deck total = {len(deck)}')
    print(f'deck[0] = {deck[0]}')
    print(f'deck[-1] = {deck[-1]}')

    print(f'Choosing a random card: {choice(deck)}')
    print(f'Choosing a random card: {choice(deck)}')
    print(f'Choosing a random card: {choice(deck)}')

    print(f'deck slicing: {deck[:6]}')
    print(f'deck slicing: {deck[12::13]}')
    slice1 = slice(0, 6)
    slice2 = slice(12, None, 13)
    print(f'deck slicing: {deck[slice1]}')
    print(f'deck slicing: {deck[slice2]}')

    shuffle(deck[slice2])
    print(f'deck shuffling: {deck[slice2]}')
