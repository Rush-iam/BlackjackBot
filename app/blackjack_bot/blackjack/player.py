from enum import auto

from app.packages.enum_generator import GeneratedStrEnum

from .deck import Deck


class PlayerState(GeneratedStrEnum):
    idle = auto()
    waiting = auto()
    playing = auto()
    completed = auto()


class PlayerResult(GeneratedStrEnum):
    none = auto()
    won = auto()
    lost = auto()
    draw = auto()


class Player:
    def __init__(self, player_id: int, name: str, balance: int):
        self.id: int = player_id
        self.name: str = name
        self.balance: int = balance
        self.bet: int = 50
        self.hand: Deck = Deck(empty=True)
        self.state: PlayerState = PlayerState.idle
        self.result: PlayerResult = PlayerResult.none

    def str_with_balance(self) -> str:
        return f'{self.name}: {self.balance}$'

    def str_with_balance_v2(self) -> str:
        return f'{self.name} ({self.balance}$)'

    def str_with_bet(self) -> str:
        return f'{self.name}: {self.bet}$'

    def str_cards(self) -> str:
        return f'{self.hand} ({self.hand.blackjack_best_value})'
