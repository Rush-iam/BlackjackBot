from app.blackjack_bot.blackjack.player import Player, PlayerState

from .base import StateHandler


class RegistrationHandler(StateHandler):
    title: str = 'Регистрация игроков'
    timer: int = 10

    def start(self) -> None:
        self.game.run_after(self.timer, self.finish)

    async def finish(self):
        if self.game.players:
            await self.game.next_state_transition()
        else:
            await self.game.finish_game()

    def handle(self, event) -> bool:
        player_id = 123

        found_player = self.game.player_find(player_id)

        if event == 'add' and not found_player:
            player = Player.get_by_id(player_id, 'player_name')
            if player.state == PlayerState.idle:
                player.state = PlayerState.waiting
                self.game.players.append(player)
                return True
        elif event == 'remove' and found_player:
            self.game.players.pop(self.game.players.index(found_player))
            found_player.state = PlayerState.idle
            return True
        return False

    def render_lines(self) -> list[str]:
        return [player.str_with_balance() for player in self.game.players]
