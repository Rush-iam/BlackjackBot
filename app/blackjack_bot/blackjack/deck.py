import itertools
import random

from typing import NamedTuple


class Card(NamedTuple):
    rank: int | str
    suit: str

    def __repr__(self) -> str:
        return f'{self.rank}{self.suit}'


class Deck:
    ranks: tuple[int | str] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K', 'A')
    values: tuple[int] = (2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11)
    suits: tuple[int] = ('♠', '♣', '♥', '♦')
    set: list[Card] = [Card(*card) for card in itertools.product(ranks, suits)]

    def __init__(self, empty: bool = False):
        self.cards: list[Card] = [] if empty else self.set

    def __repr__(self) -> str:
        return ' '.join(repr(card) for card in self.cards)

    @classmethod
    def value(cls, rank) -> int:
        return cls.values[cls.ranks.index(rank)]

    @property
    def blackjack_values(self) -> tuple[int, int]:
        min_value = 0
        max_value = 0
        for card in self.cards:
            value = self.value(card.rank)
            min_value += value if card.rank != 'A' else 1
            max_value += self.value(card.rank)
        return min_value, max_value

    @property
    def blackjack_best_value(self) -> int:
        min_value, max_value = self.blackjack_values
        if max_value <= 21:
            return max_value
        else:
            return min_value

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def take_random_card(self) -> Card | None:
        if not self.cards:
            return None
        random_index = random.randrange(len(self.cards))
        return self.cards.pop(random_index)
