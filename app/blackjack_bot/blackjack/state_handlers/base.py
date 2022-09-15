import abc
import typing

if typing.TYPE_CHECKING:
    from app.blackjack_bot.blackjack.game import Game


class StateHandler(abc.ABC):
    title: str
    timer: int

    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

    @abc.abstractmethod
    def start(self) -> None:
        ...

    @abc.abstractmethod
    def handle(self, event) -> bool:
        ...

    @abc.abstractmethod
    def render_lines(self) -> list[str]:
        ...
