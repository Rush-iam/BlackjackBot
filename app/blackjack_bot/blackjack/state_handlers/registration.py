from app.blackjack_bot.blackjack.player import Player, PlayerState
from app.blackjack_bot.telegram.inline_keyboard import InlineKeyboard, InlineButton

from .base import StateHandler


class RegistrationHandler(StateHandler):
    title: str = 'Регистрация игроков'
    timer: int = 10
    query_commands: list[str] = ['add', 'remove']

    async def start(self) -> None:
        self.game.run_after(self.timer, self.finish)

    async def finish(self):
        if self.game.players:
            await self.game.next_state_transition()
        else:
            await self.game.finish_game()

    def handle(self, player_id: int, data: str) -> tuple[bool, str | None]:
        found_player = self.game.player_find(player_id)

        if data == 'add' and not found_player:
            player = Player.get_by_id(player_id, 'player_name')
            if player.state == PlayerState.idle:
                player.state = PlayerState.waiting
                self.game.players.append(player)
                return True, 'Регистрация успешна'
        elif data == 'remove' and found_player:
            self.game.players.pop(self.game.players.index(found_player))
            found_player.state = PlayerState.idle
            return True, 'Отмена регистрации'
        return False, 'Не тыкай дважды! :)'

    def render_lines(self) -> list[str]:
        return [player.str_with_balance() for player in self.game.players]

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        keyboard = InlineKeyboard()
        keyboard[0][0] = InlineButton(text='☑', callback_data='remove')
        keyboard[0][1] = InlineButton(text='✅', callback_data='add')
        return keyboard
