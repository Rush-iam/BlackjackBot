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
    def __init__(self, player_id: int, name: str):
        self.id: int = player_id
        self.name: str = name
        self.balance: int = 1000
        self.bet: int = 50
        self.hand: Deck = Deck(empty=True)
        self.state: PlayerState = PlayerState.idle
        self.result: PlayerResult = PlayerResult.none

    @classmethod
    def get_by_id(cls, player_id: int, name: str) -> 'Player':
        # if player_id exists in db:
        # return player from db
        # else:
        return cls(player_id, name)

    def str_with_balance(self) -> str:
        return f'{self.name} ({self.balance}$)'

    def str_with_bet(self) -> str:
        return f'{self.name}: {self.bet}$'

    def str_with_cards(self) -> str:
        return f'{self.name}: {self.hand} ({self.hand.blackjack_best_value})'
