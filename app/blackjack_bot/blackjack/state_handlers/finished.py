from app.blackjack_bot.blackjack.player import PlayerResult, PlayerState
from app.blackjack_bot.telegram.dtos import User

from .base import StateHandler


class FinishedHandler(StateHandler):
    title: str = 'Игра окончена'

    async def start(self) -> None:
        for player in self.game.players:
            player.state = PlayerState.idle
        await self.game.store.finish_game(
            game_id=self.game.id, players=self.game.players
        )

    async def handle(self, tg_player: User, data: str) -> tuple[bool, str | None]:
        pass

    def render_lines(self) -> list[str]:
        if not self.game.players:
            return ['Нет игроков']

        dealer_lost = self.game.dealer.result is PlayerResult.lost
        results = [
            f'{self.game.dealer.name}{"💥" if dealer_lost else ""}',
            self.game.dealer.str_cards(),
        ]
        for player in self.game.players:
            match player.result:
                case PlayerResult.won:
                    result_value = f'+{player.bet}💰'
                case PlayerResult.lost:
                    result_value = f'-{player.bet}💥'
                case PlayerResult.draw:
                    result_value = '0➗'
                case _:
                    result_value = 'неизвестно. Как так вышло?'
            results.append(f'{player.name}: {result_value}')
            results.append(player.str_cards())
        return results
