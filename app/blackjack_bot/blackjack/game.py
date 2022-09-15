from asyncio import Task, sleep, create_task
from datetime import datetime
from enum import auto
from typing import Callable, Awaitable

from app.packages.enum_generator import GeneratedStrEnum
from app.packages.logger import logger

from .deck import Deck
from .player import Player
from .state_handlers.base import StateHandler
from .state_handlers.betting import BettingHandler
from .state_handlers.finished import FinishedHandler
from .state_handlers.playing import PlayingHandler
from .state_handlers.registration import RegistrationHandler


class GameState(GeneratedStrEnum):
    registration = auto()
    betting = auto()
    playing = auto()
    finished = auto()


class Game:
    def __init__(
        self, game_id: int | str, message_editor: Callable[[str], Awaitable[None]]
    ):
        self.id: int | str = game_id
        self.message_editor: Callable[[str], Awaitable[None]] = message_editor
        self.start_time: datetime = datetime.now()
        self.end_time: datetime | None = None
        self.tasks_ref: set[Task] = set()  # protects Task from garbage collector

        self.next_states: list[tuple[GameState, StateHandler]] = [
            (GameState.registration, RegistrationHandler(self)),
            (GameState.betting, BettingHandler(self)),
            (GameState.playing, PlayingHandler(self)),
            (GameState.finished, FinishedHandler(self)),
        ]
        self.state: GameState | None = None
        self.state_handler: StateHandler | None = None

        self.players: list[Player] = []
        self.dealer: Player = Player(player_id=0, name='Дилер')
        self.deck: Deck = Deck()
        self.round: int = 0

    def player_find(self, player_id: int) -> Player | None:
        return next((player for player in self.players if player.id == player_id), None)

    async def start(self) -> None:
        await self.next_state_transition()

    async def next_state_transition(self) -> None:
        logger.info('[%s] %s -> %s', self.id, self.state, self.next_states[0][0])
        self.state, self.state_handler = self.next_states.pop(0)
        self.state_handler.start()
        await self.render_message()

    async def handle_event(self, event) -> None:
        is_updated = self.state_handler.handle(event)
        if is_updated:
            await self.render_message()

    async def finish_game(self) -> None:
        while self.next_states:
            self.state, self.state_handler = self.next_states.pop(0)
        self.end_time = datetime.now()
        await self.render_message()

    async def render_message(self):
        title = self.state_handler.title
        logger.info('[%s] %s', self.id, title)
        lines = '\n'.join(self.state_handler.render_lines())
        message_text = f'🃏 {title}\n\n{lines}'
        await self.message_editor(message_text)

    def run_after(self, seconds: int, function: Callable[[], Awaitable[None]]) -> Task:
        async def _run_after() -> None:
            await sleep(seconds)
            await function()
        task = create_task(_run_after())
        self.tasks_ref.add(task)
        task.add_done_callback(self.tasks_ref.discard)
        logger.info(
            '[%s] seconds: %d, function: %s', self.id, seconds, function.__name__
        )
        return task
