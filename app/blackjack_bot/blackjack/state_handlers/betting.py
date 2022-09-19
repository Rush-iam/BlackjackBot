import logging

from app.blackjack_bot.telegram.dtos import User
from app.blackjack_bot.telegram.inline_keyboard import InlineButton, InlineKeyboard

from .base import StateHandler


class BettingHandler(StateHandler):
    title: str = 'Ваши ставки, господа'
    timer: int = 10
    bet_step: int = 10
    query_commands: list[str] = ['up', 'down']

    async def start(self) -> None:
        self.game.run_after(self.timer, self.game.next_state_transition)

    async def handle(self, tg_player: User, data: str) -> tuple[bool, str | None]:
        player = self.game.player_find(tg_player.id)
        if not player:
            return False, 'Не получится, Вас нет в игре'

        if data == 'up':
            if player.balance >= player.bet + self.bet_step:
                player.bet += self.bet_step
                return True, f'Ставка ➕{self.bet_step}$'
            else:
                return False, 'Никак - уже ва-банк!'
        elif data == 'down':
            if player.bet - self.bet_step > 0:
                player.bet -= self.bet_step
                return True, f'Ставка ➖{self.bet_step}$'
            else:
                return False, 'Здесь серьёзное заведение'

        logging.warning('unknown data: %s', data)
        return False, ''

    def render_lines(self) -> list[str]:
        return [player.str_with_bet() for player in self.game.players]

    @staticmethod
    def render_keyboard() -> InlineKeyboard:
        keyboard = InlineKeyboard()
        keyboard[0][0] = InlineButton(text='➖', callback_data='down')
        keyboard[0][1] = InlineButton(text='➕', callback_data='up')
        return keyboard
