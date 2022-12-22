from enum import StrEnum, auto

from app.blackjack_bot.bot.message_editor import MessageEditor
from app.blackjack_bot.telegram.dtos import User
from app.packages.logger import logger

from .deck import Deck
from .player import Player, PlayerState
from .state_handlers.base import StateHandler
from .state_handlers.betting import BettingHandler
from .state_handlers.finished import FinishedHandler
from .state_handlers.playing import PlayingHandler
from .state_handlers.registration import RegistrationHandler
from .store import BlackjackStore
from .timer import Timer


class GameState(StrEnum):
    registration = auto()
    betting = auto()
    playing = auto()
    finished = auto()


class Game:
    def __init__(
        self,
        game_id: int,
        chat_id: int | str,
        game_message: MessageEditor,
        timer_message: MessageEditor | None,
        store: BlackjackStore,
    ):
        self.id: int = game_id
        self.chat_id: int | str = chat_id
        self.game_message: MessageEditor = game_message
        self.timer: Timer = Timer(timer_message)

        self.next_states: list[tuple[GameState, StateHandler]] = [
            (GameState.registration, RegistrationHandler(self)),
            (GameState.betting, BettingHandler(self)),
            (GameState.playing, PlayingHandler(self)),
            (GameState.finished, FinishedHandler(self)),
        ]
        self.state: GameState | None = None
        self.state_handler: StateHandler | None = None

        self.players: list[Player] = []
        self.dealer: Player = Player(player_id=0, name='Дилер', balance=0)
        self.deck: Deck = Deck()
        self.round: int = 0

        self.store: BlackjackStore = store

    def player_find(self, player_id: int) -> Player | None:
        return next((player for player in self.players if player.id == player_id), None)

    async def start(self) -> None:
        await self.next_state_transition()

    async def next_state_transition(self) -> None:
        logger.info('[%s] %s -> %s', self.id, self.state, self.next_states[0][0])
        self.state, self.state_handler = self.next_states.pop(0)
        await self.state_handler.start()

    async def handle_event(self, tg_player: User, data: str) -> str | None:
        if not self.state_handler:
            raise Exception(
                f'{self.__class__.__name__}: {self.handle_event.__name__}: '
                f'state handler not set'
            )

        if data not in self.state_handler.query_commands:
            logger.warning('no handler for query data: %s', data)
            return None
        is_updated, answer = await self.state_handler.handle(tg_player, data)
        if is_updated:
            await self.render_message()  # stack up render requests in 1sec delay buffer
        return answer

    async def finish_game(self) -> None:
        while self.next_states:
            self.state, self.state_handler = self.next_states.pop(0)
        for player in self.players:
            player.state = PlayerState.idle
        await self.store.finish_game(game_id=self.id, players=self.players)
        await self.timer.delete()
        await self.render_message()

    async def render_message(self):
        title = self.state_handler.title
        logger.info('[%s] %s', self.id, title)
        lines = '\n'.join(self.state_handler.render_lines())
        message_text = f'🃏 {title}\n\n{lines}'

        keyboard = self.state_handler.render_keyboard()
        await self.game_message(message_text, keyboard)
