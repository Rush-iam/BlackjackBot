import abc
import typing

from app.blackjack_bot.telegram.inline_keyboard import InlineKeyboard

if typing.TYPE_CHECKING:
    from app.blackjack_bot.blackjack.game import Game


class StateHandler(abc.ABC):
    title: str
    timer: int
    query_commands: list[str] = []

    def __init__(self, game: 'Game'):
        self.game: 'Game' = game

    @abc.abstractmethod
    async def start(self) -> None:
        ...

    @abc.abstractmethod
    def handle(self, from_id: int, data: str) -> tuple[bool, str | None]:
        ...

    @abc.abstractmethod
    def render_lines(self) -> list[str]:
        ...

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        ...
