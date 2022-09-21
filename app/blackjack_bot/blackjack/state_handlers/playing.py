import itertools
from asyncio import Task

from app.blackjack_bot.blackjack.player import Player, PlayerResult, PlayerState
from app.blackjack_bot.telegram.dtos import User
from app.blackjack_bot.telegram.inline_keyboard import InlineButton, InlineKeyboard

from .base import StateHandler


class PlayingHandler(StateHandler):
    title: str = 'Ещё карту?'
    timer: int = 10
    timer_task: Task | None = None
    query_commands: list[str] = ['hit', 'stand']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_player: Player | None = None

    async def start(self) -> None:
        self.game.dealer.hand.add_card(self.game.deck.take_random_card())
        for player in self.game.players:
            player.hand.add_card(self.game.deck.take_random_card())
            player.hand.add_card(self.game.deck.take_random_card())
        await self.next_round_transition()

    async def finish(self) -> None:
        while True:
            self.game.dealer.hand.add_card(self.game.deck.take_random_card())
            dealer_min, dealer_max = self.game.dealer.hand.blackjack_values
            if dealer_min >= 16 or dealer_max == 21:
                break
            # TODO: emulate 1 sec delay?

        dealer_score = self.game.dealer.hand.blackjack_best_value
        if dealer_lost := dealer_score > 21:
            self.game.dealer.result = PlayerResult.lost

        for player in self.game.players:
            player_score = player.hand.blackjack_best_value
            player_lost = player_score > 21
            if player_lost:
                player.result = PlayerResult.draw if dealer_lost else PlayerResult.lost
            else:
                if dealer_score < player_score or dealer_lost:
                    player.result = PlayerResult.won
                elif dealer_score == player_score:
                    player.result = PlayerResult.draw
                else:
                    player.result = PlayerResult.lost
            if player.result is PlayerResult.won:  # TODO: гонка с параллельной игрой
                player.balance += player.bet
            elif player.result is PlayerResult.lost:
                player.balance -= player.bet

        await self.game.next_state_transition()

    async def handle(self, tg_player: User, data: str) -> tuple[bool, str | None]:
        if not self.current_player:
            raise Exception('PlayingHandler: handle: no current player')

        if self.current_player.id != tg_player.id:
            return False, 'Погоди-ка, это не твой ход'

        if self.timer_task:
            self.timer_task.cancel()
        player = self.current_player
        if data == 'hit':
            player.hand.add_card(self.game.deck.take_random_card())
            min_value, max_value = player.hand.blackjack_values
            if min_value > 21:
                player.state = PlayerState.completed
            else:
                player.state = PlayerState.waiting
        elif data == 'stand':
            player.state = PlayerState.completed

        await self.next_player_transition(force_render=True)
        return False, None

    async def next_round_transition(self, force_render: bool = False) -> None:
        active_players_count = 0
        for player in self.game.players:
            if player.state is PlayerState.waiting:
                player.state = PlayerState.playing
                active_players_count += 1
        if active_players_count:
            self.game.round += 1
            await self.next_player_transition(force_render)
        else:
            await self.finish()

    async def next_player_transition(self, force_render: bool = False) -> None:
        player = self.get_next_active_player()
        if not player:
            await self.next_round_transition(force_render)
            return

        self.current_player = player
        self.timer_task = self.game.run_after(self.timer, self.player_timeout)
        if force_render:
            await self.game.render_message()

    def get_next_active_player(self) -> Player | None:
        return next(
            (
                player
                for player in self.game.players
                if player.state is PlayerState.playing
            ),
            None,
        )

    async def player_timeout(self) -> None:
        if self.current_player:
            self.current_player.state = PlayerState.completed
        await self.next_player_transition(force_render=True)

    def render_lines(self) -> list[str]:
        lines: list[str] = []
        lines.extend(
            f'{player.name}\n{player.str_cards()}'
            for player in itertools.chain([self.game.dealer], self.game.players)
        )
        lines.append('')
        if self.current_player:
            lines.append(f'{self.current_player.name}, ещё карту?')
        return lines

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        keyboard = InlineKeyboard()
        keyboard[0][0] = InlineButton(text='☝', callback_data='hit')
        keyboard[0][1] = InlineButton(text='🤚', callback_data='stand')
        return keyboard
