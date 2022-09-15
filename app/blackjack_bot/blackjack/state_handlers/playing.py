import itertools
from asyncio import Task

from app.blackjack_bot.blackjack.player import Player, PlayerResult, PlayerState

from .base import StateHandler


class PlayingHandler(StateHandler):
    title: str = 'Blackjack'
    timer: int = 10
    timer_task: Task | None = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_player: Player | None = None

    def start(self) -> None:
        self.game.dealer.hand.add_card(self.game.deck.take_random_card())
        self.next_round_transition()

    async def finish(self):
        dealer_min, dealer_max = self.game.dealer.hand.blackjack_values
        while dealer_min < 16 and dealer_max != 21:
            self.game.dealer.hand.add_card(self.game.deck.take_random_card())
            # TODO: emulate 1 sec delay?

        dealer_score = self.game.dealer.hand.blackjack_best_value
        dealer_lost = dealer_score > 21

        for player in self.game.players:
            player_score = player.hand.blackjack_best_value
            player_lost = player_score > 21
            if player_lost:
                player.result = PlayerResult.draw if dealer_lost else PlayerResult.lost
            else:
                if dealer_score < player_score:
                    player.result = PlayerResult.won
                elif dealer_score == player_score:
                    player.result = PlayerResult.draw
                else:
                    player.result = PlayerResult.lost

        await self.game.next_state_transition()

    def handle(self, event) -> bool:
        player_id = 123

        if self.current_player.id != player_id:
            return False

        self.timer_task.cancel()
        player = self.current_player
        if event == 'hit':
            player.hand.add_card(self.game.deck.take_random_card())
            min_value, max_value = player.hand.blackjack_values
            if min_value > 21:
                player.state = PlayerState.completed
            else:
                player.state = PlayerState.waiting
        elif event == 'stand':
            player.state = PlayerState.completed

        self.next_player_transition()
        return True

    async def next_round_transition(self) -> None:
        active_players_count = 0
        for player in self.game.players:
            if player.state is PlayerState.waiting:
                player.state = PlayerState.playing
                active_players_count += 1
        if active_players_count:
            self.game.round += 1
            return await self.next_player_transition()
        else:
            return await self.finish()

    async def next_player_transition(self) -> None:
        player = self.get_next_active_player()
        if not player:
            return await self.next_round_transition()

        self.current_player = player
        self.timer_task = self.game.run_after(self.timer, self.player_timeout)

    def get_next_active_player(self) -> Player | None:
        return next(
            (
                player for player in self.game.players
                if player.state is PlayerState.playing
            ), None
        )

    async def player_timeout(self):
        self.current_player.state = PlayerState.completed
        await self.next_player_transition()
        await self.game.render_message()

    def render_lines(self) -> list[str]:
        return [
            player.str_with_cards()
            for player in itertools.chain([self.game.dealer], self.game.players)
        ]
