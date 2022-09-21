import itertools
import random
from typing import NamedTuple


class Card(NamedTuple):
    rank: str
    suit: str

    def __repr__(self) -> str:
        return f'{Deck.rank_emojis[self.rank]}{self.suit}'

    @property
    def value(self) -> int:
        return Deck.ranks[self.rank]


class Deck:
    ranks: dict[str, int] = {
        '2': 2,
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        '10': 10,
        'J': 10,
        'Q': 10,
        'K': 10,
        'A': 11,
    }
    rank_emojis: dict[str, str] = {
        '2': '2️⃣',
        '3': '3️⃣',
        '4': '4️⃣',
        '5': '5️⃣',
        '6': '6️⃣',
        '7': '7️⃣',
        '8': '8️⃣',
        '9': '9️⃣',
        '10': '🔟',
        'J': '🤵',
        'Q': '👰‍',
        'K': '🤴',
        'A': '🅰',
    }
    suits: tuple[str, ...] = ('♠', '♣', '♥', '♦')
    set: list[Card] = [Card(*card) for card in itertools.product(ranks.keys(), suits)]

    def __init__(self, empty: bool = False):
        self.cards: list[Card] = [] if empty else self.set

    def __repr__(self) -> str:
        return ' '.join(repr(card) for card in self.cards)

    @property
    def blackjack_values(self) -> tuple[int, int]:
        min_value = 0
        max_value = 0
        for card in self.cards:
            value = card.value
            min_value += value if card.rank != 'A' else 1
            max_value += card.value
        return min_value, max_value

    @property
    def blackjack_best_value(self) -> int:
        min_value, max_value = self.blackjack_values
        if max_value <= 21:
            return max_value
        return min_value

    def add_card(self, card: Card) -> None:
        self.cards.append(card)

    def take_random_card(self) -> Card | None:
        if not self.cards:
            return None
        random_index = random.randrange(len(self.cards))
        return self.cards.pop(random_index)
