from app.blackjack_bot.blackjack.player import PlayerState, PlayerResult
from app.blackjack_bot.telegram.dtos import User

from .base import StateHandler


class FinishedHandler(StateHandler):
    title: str = 'Игра окончена'

    async def start(self) -> None:
        for player in self.game.players:
            player.state = PlayerState.idle

    async def handle(self, player: User, data: str) -> tuple[bool, str | None]:
        pass

    def render_lines(self) -> list[str]:
        if not self.game.players:
            return ['Нет игроков']

        dealer_lost = self.game.dealer.result is PlayerResult.lost
        dealer_with_cards = self.game.dealer.str_with_cards()
        if dealer_lost:
            dealer_with_cards += '💥'

        results = [dealer_with_cards]
        for player in self.game.players:
            match player.result:
                case PlayerResult.won:
                    result = f'💰{player.bet}$'
                case PlayerResult.lost:
                    result = f'💥-{player.bet}$'
                case PlayerResult.draw:
                    result = f'0️⃣$'
                case _:
                    result = 'неизвестно. Как так вышло?'
            results.append(f'{player.str_with_cards()}  {result}')
        return results
