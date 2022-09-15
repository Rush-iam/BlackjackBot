from app.blackjack_bot.blackjack.player import PlayerState, PlayerResult

from .base import StateHandler


class FinishedHandler(StateHandler):
    title: str = 'Игра окончена'

    def start(self) -> None:
        for player in self.game.players:
            player.state = PlayerState.idle

    def handle(self, event) -> bool:
        pass

    def render_lines(self) -> list[str]:
        if not self.game.players:
            return ['Нет игроков']

        dealer_with_cards = self.game.dealer.str_with_cards()
        results = [dealer_with_cards]
        for player in self.game.players:
            match player.result:
                case PlayerResult.won:
                    result = f'+{player.bet}$'
                case PlayerResult.lost:
                    result = f'-{player.bet}$'
                case PlayerResult.draw:
                    result = f'=0$'
                case _:
                    result = 'неизвестно'
            results.append(f'{player.str_with_cards()}: {result}')
        return results
