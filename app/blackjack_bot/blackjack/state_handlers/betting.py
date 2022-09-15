from .base import StateHandler


class BettingHandler(StateHandler):
    title: str = 'Делаем ставки!'
    timer: int = 10
    bet_step: int = 5
    query_commands: list[str] = ['up', 'down']

    async def start(self) -> None:
        self.game.run_after(self.timer, self.game.next_state_transition)

    def handle(self, player_id: int, data: str) -> tuple[bool, str | None]:
        player = self.game.player_find(player_id)
        if not player:
            return False, 'Вас нет в этой игре'

        if data == 'up':
            player.bet += self.bet_step
            return True, f'Ставка +{self.bet_step}$'
        elif data == 'down':
            player.bet -= self.bet_step
            return True, f'Ставка -{self.bet_step}$'

    def render_lines(self) -> list[str]:
        return [player.str_with_bet() for player in self.game.players]
