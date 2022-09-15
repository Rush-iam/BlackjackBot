from .base import StateHandler


class BettingHandler(StateHandler):
    title: str = 'Делаем ставки!'
    timer: int = 10
    bet_step: int = 5

    def start(self) -> None:
        self.game.run_after(self.timer, self.game.next_state_transition)

    def handle(self, event) -> bool:
        player_id = 123

        player = self.game.player_find(player_id)
        if not player:
            return False

        if event == 'up':
            player.bet += self.bet_step
        elif event == 'down':
            player.bet -= self.bet_step
        return True

    def render_lines(self) -> list[str]:
        return [player.str_with_bet() for player in self.game.players]
