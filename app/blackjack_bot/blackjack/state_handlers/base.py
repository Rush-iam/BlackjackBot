import abc
import typing

from app.blackjack_bot.bot.inline_keyboard import InlineKeyboard
from app.blackjack_bot.telegram.dtos import User


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
    async def handle(self, tg_player: User, data: str) -> tuple[bool, str | None]:
        ...

    @abc.abstractmethod
    def render_lines(self) -> list[str]:
        ...

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        ...
